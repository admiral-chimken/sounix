"""Sounix glue: model-selection and voice commands for respond().

Needs models.py and voice.py in the same folder. Nothing changes until you use
a model or voice command; "default model" returns to your old ask_ollama path.
"""
from __future__ import annotations

import json
import re
import threading
from pathlib import Path

from models import TASKS, ModelRouter, OllamaError

router = ModelRouter()
SETTINGS_PATH = Path.home() / ".sounix" / "settings.json"
_VOICE_KEYS = {"wake_phrase": str, "silent_threshold": int, "source": str, "capture": str}


def _load_settings() -> dict:
    try:
        data = json.loads(SETTINGS_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


_saved = _load_settings()
_enabled = bool(_saved.get("routing_enabled", router.pinned is not None))


def _save_settings() -> None:
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps({"routing_enabled": _enabled, "voice": _opts}, indent=2))
    except OSError:
        pass


def _set_enabled(value: bool) -> None:
    global _enabled
    _enabled = value
    _save_settings()
voice_output = print                      # GUI: ai_control.voice_output = your_function
_history: list[dict] = []
SYSTEM = ("You are Sounix, a cybersecurity-focused assistant for Linux. "
          "Be concise, practical, and safe.")

MODELS_HELP = """========== MODEL HELP ==========

models                      list installed models (tier, size)
use model <name>            pin one, e.g. use model llama 3.1 8b
use fast model              pin your smallest model
use balanced model          pin a mid-size model
use deep model              pin your biggest model
automatic model             Sounix picks a model for each task
default model               back to your original setup
task model <task> <name>    always use <name> for a task
                            tasks: chat, triage, log_analysis,
                            code_audit, threat_report, reasoning
Note: "set model" / "model status" are your older preference system;
they apply while "default model" is active."""

VOICE_HELP = """========== VOICE HELP ==========

voice on / voice off / voice status
voice wake <phrase>         change the wake phrase (default: hey sounix)
voice threshold <number>    mic sensitivity, lower = more sensitive (default 750)
voice source <name or id>   choose a PipeWire mic ("voice source default" to reset)
voice reset                forget saved voice settings

Say the wake phrase, then a command. Say "end sounix" to stop listening.
For safety, risky commands (shutdown, delete, install, firewall changes,
yes/no confirmations) must be typed, not spoken.
Setup: sudo apt install libportaudio2 && pip install sounddevice numpy faster-whisper"""


def _msg(exc: Exception) -> str:
    return f"Sounix: {exc.args[0] if isinstance(exc, KeyError) and exc.args else exc}"


def _state() -> str:
    if not _enabled:
        return "default (your original ask_ollama setup)"
    return f"pinned to {router.pinned}" if router.pinned else "automatic (model chosen per task)"


# ---- model commands ---------------------------------------------------
def model_command(command: str, original: str):
    global _enabled
    try:
        if command in {"models", "list models", "installed models"}:
            return ("Sounix: Installed models (* = pinned):\n" + router.describe()
                    + f"\n\nRouting: {_state()}")
        if command == "help models":
            return MODELS_HELP
        if command in {"use fast model", "use balanced model", "use deep model"}:
            tier = command.split()[1]
            m = router.use_tier(tier)
            router.save()
            _set_enabled(True)
            return f"Sounix: Using {m.name} ({tier})."
        if command == "use model":
            return "Sounix: Use: use model <name>   (type 'models' to see them)"
        if command.startswith("use model "):
            m = router.use(command[10:].strip(), persist=True)
            _set_enabled(True)
            return f"Sounix: Using {m.name}."
        if command in {"automatic model", "auto model"}:
            router.use(None, persist=True)
            _set_enabled(True)
            return "Sounix: Automatic model selection is on."
        if command == "default model":
            _set_enabled(False)
            return "Sounix: Back to your default model setup."
        if command.startswith("task model "):
            parts = command[11:].split(maxsplit=1)
            if len(parts) != 2 or parts[0] not in TASKS:
                return "Sounix: Use: task model <task> <name>\nTasks: " + ", ".join(TASKS)
            router.set_task_model(parts[0], parts[1])
            return f"Sounix: {parts[0]} will use {router.overrides[parts[0]]}."
    except (OllamaError, KeyError, ValueError) as exc:
        return _msg(exc)
    return None


def _task_for(message: str) -> str:
    m = message.lower()
    if re.search(r"\b(audit|source code|python code|script|function|exploit code)\b", m):
        return "code_audit"
    if re.search(r"\b(logs?|auth\.log|syslog|journalctl)\b", m):
        return "log_analysis"
    if re.search(r"\breport\b", m):
        return "threat_report"
    return "chat"


def smart_ask(message: str, fallback):
    """Use the router when enabled; otherwise (or on failure) your original ask_ollama."""
    if not _enabled:
        return fallback(message)
    try:
        text, model = router.complete(message, system=SYSTEM, task=_task_for(message),
                                      history=_history)
    except (OllamaError, KeyError, ValueError) as exc:
        print(f"[router] {_msg(exc)}; using default model")
        return fallback(message)
    _history.extend([{"role": "user", "content": message},
                     {"role": "assistant", "content": text}])
    del _history[:-12]
    return f"{text}\n\n[model: {model}]"


# ---- voice commands ---------------------------------------------------
_BLOCKED = ("yes", "y", "shutdown", "restart", "delete", "install", "enable firewall",
            "disable firewall", "update sounix", "move", "rename", "copy",
            "make folder", "remember", "forget")
_saved_voice = _saved.get("voice") if isinstance(_saved.get("voice"), dict) else {}
_opts: dict = {k: v for k, v in _saved_voice.items()
               if k in _VOICE_KEYS and isinstance(v, _VOICE_KEYS[k])}
_voice = {"listener": None, "running": False}


def _heard(text: str, respond) -> None:
    t = text.strip()
    if any(t == b or t.startswith(b + " ") for b in _BLOCKED):
        out = "Sounix: For safety, that command must be typed, not spoken."
    else:
        out = respond(t)
    voice_output(f'[voice] "{t}"\n{out}')


def _start(respond) -> str:
    if _voice["running"]:
        return "Sounix: Voice is already on."
    try:
        from voice import VoiceConfig, VoiceListener
    except Exception as exc:
        return (f"Sounix: Voice needs extra packages ({exc}).\n"
                "Run: sudo apt install libportaudio2 && pip install sounddevice numpy faster-whisper")
    _voice["running"] = True

    def run():
        try:
            _voice["listener"] = VoiceListener(lambda t: _heard(t, respond), VoiceConfig(**_opts))
            _voice["listener"].start()
        except Exception as exc:
            voice_output(f"Sounix: Voice stopped: {exc}")
        finally:
            _voice["listener"], _voice["running"] = None, False

    threading.Thread(target=run, daemon=True).start()
    wake = _opts.get("wake_phrase", "hey sounix")
    return f'Sounix: Voice starting (first run downloads the speech model). Say "{wake}".'


def voice_command(command: str, original: str, respond):
    if command == "help voice":
        return VOICE_HELP
    if command in {"voice on", "start voice", "voice start"}:
        return _start(respond)
    if command in {"voice off", "stop voice", "voice stop"}:
        if _voice["listener"] is None and not _voice["running"]:
            return "Sounix: Voice is not running."
        if _voice["listener"] is not None:
            _voice["listener"].stop()
        return "Sounix: Voice stopping."
    if command == "voice reset":
        _opts.clear()
        _save_settings()
        return "Sounix: Saved voice settings cleared. Turn voice off and on to apply."
    if command == "voice status":
        lis = _voice["listener"]
        if not _voice["running"]:
            return "Sounix: Voice is off."
        if lis is None:
            return "Sounix: Voice is starting."
        mode = "listening to you" if lis.active else "waiting for the wake phrase"
        return (f"Sounix: Voice is on ({mode}). Mic level: {int(lis.last_level)} "
                f"(needs {lis.cfg.silent_threshold}+ to hear speech).")
    for key, field, cast in (("voice wake ", "wake_phrase", str),
                             ("voice threshold ", "silent_threshold", int),
                             ("voice source ", "source", str),
                             ("voice capture ", "capture", str)):
        if command.startswith(key):
            raw = original.strip()
            text = raw[len(key):] if raw.lower().startswith(key) else command[len(key):]
            try:
                value = cast(text.strip())
            except ValueError:
                return f"Sounix: Use: {key}<value>"
            if field == "source" and value.lower() in {"default", "auto", "none"}:
                value = ""
            _opts[field] = value
            _save_settings()
            if _voice["listener"] is not None:
                setattr(_voice["listener"].cfg, field, value)
            if field in {"source", "capture"}:
                return f"Sounix: {field} set to {value or 'default'}. Turn voice off and on to apply."
            return f"Sounix: {field} set to {value}."
    return None
