"""Sounix model selection for Ollama.

- Discovers installed models via /api/tags and sorts them into tiers by size.
- Routes each task type (triage, log analysis, code audit...) to a suitable model.
- Pin a model manually, override per task, fall back automatically, optionally pull.
- Per-task context size / temperature, keep_alive, and streaming.
- Stdlib only.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

CONFIG_PATH = Path.home() / ".sounix" / "models.json"


# ---- installed models ------------------------------------------------
@dataclass
class InstalledModel:
    name: str
    params_b: float          # billions of parameters (0 if unknown)
    family: str = ""
    quant: str = ""
    size_gb: float = 0.0
    tags: set = field(default_factory=set)

    @property
    def tier(self) -> str:
        if self.params_b == 0:
            return "balanced"
        return "fast" if self.params_b < 5 else "balanced" if self.params_b <= 20 else "deep"


def _parse_params(s: str) -> float:
    m = re.match(r"([\d.]+)\s*([BMK])", (s or "").upper())
    if not m:
        return 0.0
    return float(m.group(1)) * {"B": 1, "M": 1e-3, "K": 1e-6}[m.group(2)]


def _tags_for(name: str) -> set:
    n, tags = name.lower(), set()
    if re.search(r"coder|codellama|codegemma|starcoder|devstral", n): tags.add("code")
    if re.search(r"r1|qwq|reason|phi4-reasoning|magistral", n): tags.add("reasoning")
    if re.search(r"embed|bge|minilm|arctic-embed", n): tags.add("embed")
    if re.search(r"llava|vision|-vl|minicpm-v", n): tags.add("vision")
    return tags


# ---- Ollama client ---------------------------------------------------
class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, host: str | None = None):
        self.host = (host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")).rstrip("/")
        if not self.host.startswith("http"):
            self.host = "http://" + self.host

    def _open(self, path: str, body: dict | None = None, timeout: int = 300):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.host + path, data,
                                     {"Content-Type": "application/json"} if data else {})
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.URLError as exc:
            raise OllamaError(f"Can't reach Ollama at {self.host} (is `ollama serve` running?): {exc}")

    def list_models(self) -> list[InstalledModel]:
        with self._open("/api/tags", timeout=10) as r:
            raw = json.load(r).get("models", [])
        out = []
        for m in raw:
            d = m.get("details", {})
            out.append(InstalledModel(
                name=m["name"], params_b=_parse_params(d.get("parameter_size", "")),
                family=d.get("family", ""), quant=d.get("quantization_level", ""),
                size_gb=round(m.get("size", 0) / 1e9, 1), tags=_tags_for(m["name"])))
        return out

    def running(self) -> list[str]:
        with self._open("/api/ps", timeout=10) as r:
            return [m["name"] for m in json.load(r).get("models", [])]

    def chat_stream(self, model: str, messages: list, options: dict, keep_alive: str) -> Iterator[str]:
        body = {"model": model, "messages": messages, "stream": True,
                "options": options, "keep_alive": keep_alive}
        with self._open("/api/chat", body) as r:
            for line in r:
                if not line.strip():
                    continue
                chunk = json.loads(line)
                if "error" in chunk:
                    raise OllamaError(chunk["error"])
                yield chunk.get("message", {}).get("content", "")
                if chunk.get("done"):
                    return

    def pull(self, name: str, progress: Callable[[str, float], None] | None = None) -> None:
        with self._open("/api/pull", {"model": name, "stream": True}, timeout=3600) as r:
            for line in r:
                c = json.loads(line) if line.strip() else {}
                if "error" in c:
                    raise OllamaError(c["error"])
                if progress:
                    t, done = c.get("total") or 0, c.get("completed") or 0
                    progress(c.get("status", ""), done / t if t else 0.0)


# ---- routing ---------------------------------------------------------
@dataclass(frozen=True)
class Profile:
    tier: str
    num_ctx: int
    temperature: float
    prefer: tuple = ()       # preferred tags, e.g. ("code",)


TASKS = {
    "chat":          Profile("fast", 4096, 0.3),
    "triage":        Profile("fast", 4096, 0.1),
    "log_analysis":  Profile("balanced", 16384, 0.1),
    "code_audit":    Profile("deep", 16384, 0.1, ("code",)),
    "threat_report": Profile("deep", 8192, 0.4),
    "reasoning":     Profile("deep", 8192, 0.2, ("reasoning",)),
}
TIERS = ["fast", "balanced", "deep"]
_THINK = re.compile(r"<think>.*?</think>\s*", re.S)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


class ModelRouter:
    def __init__(self, client: OllamaClient | None = None, auto_pull: bool = False,
                 keep_alive: str = "10m", load_config: bool = True):
        self.client = client or OllamaClient()
        self.auto_pull = auto_pull
        self.keep_alive = keep_alive
        self.pinned: str | None = None              # manual override (beats everything)
        self.overrides: dict[str, str] = {}         # task -> model name
        self.last_model: str | None = None
        self._cache: tuple[float, list[InstalledModel]] = (0.0, [])
        if load_config:
            self._load()

    # -- config persistence --
    def _load(self) -> None:
        try:
            cfg = json.loads(CONFIG_PATH.read_text())
            self.pinned, self.overrides = cfg.get("pinned"), cfg.get("overrides", {})
        except (OSError, ValueError):
            pass

    def save(self) -> None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(json.dumps({"pinned": self.pinned, "overrides": self.overrides}, indent=2))

    # -- discovery --
    def installed(self, refresh: bool = False) -> list[InstalledModel]:
        if refresh or time.time() - self._cache[0] > 30:
            models = [m for m in self.client.list_models() if not ({"embed", "vision"} & m.tags)]
            self._cache = (time.time(), models)
        return self._cache[1]

    def resolve(self, spoken: str) -> InstalledModel | None:
        """Match a typed or spoken name loosely: 'llama 3.1 8b' -> 'llama3.1:8b'."""
        want, models = _norm(spoken), self.installed()
        for m in models:
            if _norm(m.name) == want:
                return m
        hits = [m for m in models if want and want in _norm(m.name)]
        return min(hits, key=lambda m: len(m.name)) if len(hits) >= 1 else None

    def use(self, name: str | None, persist: bool = False) -> InstalledModel | None:
        """Pin a model (loose name match) or None for automatic routing."""
        m = None
        if name is not None:
            m = self.resolve(name)
            if not m:
                raise KeyError(f"No installed model matches '{name}'")
        self.pinned = m.name if m else None
        if persist:
            self.save()
        return m

    def use_tier(self, tier: str) -> InstalledModel:
        pool = [m for m in self.installed() if m.tier == tier] or self.installed()
        pick = max(pool, key=lambda m: m.params_b) if tier == "deep" else min(pool, key=lambda m: m.params_b)
        self.pinned = pick.name
        return pick

    def set_task_model(self, task: str, name: str) -> None:
        m = self.resolve(name)
        if not m:
            raise KeyError(f"No installed model matches '{name}'")
        self.overrides[task] = m.name
        self.save()

    def candidates(self, task: str = "chat") -> list[InstalledModel]:
        prof = TASKS.get(task, TASKS["chat"])
        models, t_idx = self.installed(), TIERS.index(prof.tier)

        def key(m: InstalledModel):
            missing_pref = 0 if set(prof.prefer) & m.tags else 1 if prof.prefer else 0
            # specialists (code / reasoning) shouldn't win tasks that didn't ask for them
            if (m.tags & {"code", "reasoning"}) - set(prof.prefer):
                missing_pref += 1
            dist = abs(TIERS.index(m.tier) - t_idx)
            size = -m.params_b if t_idx >= 1 else m.params_b   # bigger for deep, smaller for fast
            return (missing_pref, dist, size)

        ordered = sorted(models, key=key)
        first = [self.pinned] if self.pinned else []
        if task in self.overrides:
            first.append(self.overrides[task])
        head = [m for n in first for m in models if m.name == n]
        return head + [m for m in ordered if m not in head]

    # -- running --
    def _messages(self, prompt, system, history):
        msgs = [{"role": "system", "content": system}] if system else []
        return msgs + list(history or []) + [{"role": "user", "content": prompt}]

    def stream(self, prompt: str, system: str = "", task: str = "chat", history=None,
               model: str | None = None) -> Iterator[str]:
        prof = TASKS.get(task, TASKS["chat"])
        opts = {"num_ctx": prof.num_ctx, "temperature": prof.temperature}
        order = [self.resolve(model)] if model and self.resolve(model) else self.candidates(task)
        if not order:
            raise OllamaError("No models installed. Run e.g. `ollama pull llama3.1:8b`.")
        errors = []
        for m in order:
            started = False
            try:
                for piece in self.client.chat_stream(m.name, self._messages(prompt, system, history),
                                                     opts, self.keep_alive):
                    started = True
                    self.last_model = m.name
                    yield piece
                return
            except OllamaError as exc:
                errors.append(f"{m.name}: {exc}")
                if started:      # can't fall back mid-answer
                    raise
        raise OllamaError("All models failed:\n" + "\n".join(errors))

    def complete(self, prompt: str, system: str = "", task: str = "chat", history=None,
                 model: str | None = None) -> tuple[str, str]:
        text = "".join(self.stream(prompt, system, task, history, model))
        return _THINK.sub("", text).strip(), self.last_model or ""

    def ensure(self, name: str, progress=None) -> None:
        """Pull a model if it isn't installed (only when auto_pull is on)."""
        if self.resolve(name) or not self.auto_pull:
            return
        self.client.pull(name, progress)
        self.installed(refresh=True)

    def describe(self) -> str:
        rows = [f"{'*' if m.name == self.pinned else ' '} {m.name:<28} {m.tier:<9} "
                f"{m.params_b:>5.1f}B {m.size_gb:>5.1f}GB {','.join(sorted(m.tags))}"
                for m in sorted(self.installed(), key=lambda m: m.params_b)]
        return "\n".join(rows) or "(no models installed)"
