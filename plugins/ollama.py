"""Sounix model store: browse and download more Ollama models.

  ollama recommended       good models for this computer (shows what fits your RAM and disk)
  ollama list              models installed now
  ollama pull <name>       download a model in the background, e.g.  ollama pull llama3.1:8b
  ollama status            progress of the current download
  ollama cancel            stop the current download (it resumes if you pull it again)
  ollama help

After a download finishes, pick the model with:  use model <name>   (or: models)
"""
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

COMMAND = "ollama"

HELP = (
    "========== OLLAMA MODELS HELP ==========\n\n"
    "ollama recommended       good models for this computer (fits your RAM and disk?)\n"
    "ollama list              models installed now\n"
    "ollama pull <name>       download a model in the background, e.g. ollama pull llama3.1:8b\n"
    "ollama status            progress of the current download\n"
    "ollama cancel            stop the download (pulling it again resumes it)\n\n"
    "After a download: 'models' lists them, 'use model <name>' picks one,\n"
    "'use fast model' / 'use deep model' pick by size, 'automatic model' lets Sounix choose.\n"
    "Bigger models answer better but need more RAM and run slower."
)

# (name, download size GB, what it is good for). Sizes are approximate.
RECOMMENDED = [
    ("llama3.2:1b",       1.3, "tiny and very fast; simple questions"),
    ("llama3.2:3b",       2.0, "fast all-rounder; a good first upgrade"),
    ("qwen2.5:3b",        1.9, "fast; follows instructions well"),
    ("qwen3:4b",          2.5, "small model that can reason step by step"),
    ("gemma3:4b",         3.3, "fast and tidy answers"),
    ("mistral:7b",        4.1, "solid general model"),
    ("qwen2.5:7b",        4.7, "strong general model; good for log reviews"),
    ("qwen2.5-coder:7b",  4.7, "code audits and scripts"),
    ("deepseek-r1:7b",    4.7, "step-by-step reasoning (slower)"),
    ("llama3.1:8b",       4.9, "reliable general model; good for log reviews"),
    ("qwen3:8b",          5.2, "strong reasoning and chat"),
    ("gemma3:12b",        8.1, "deeper answers, needs more RAM"),
    ("qwen2.5:14b",       9.0, "deep tier general model"),
    ("qwen2.5-coder:14b", 9.0, "deep tier code audits"),
    ("deepseek-r1:14b",   9.0, "deep reasoning (slow)"),
]

NAME_OK = re.compile(r"^[a-z0-9][a-z0-9._\-]*(/[a-z0-9][a-z0-9._\-]*)*(:[A-Za-z0-9][A-Za-z0-9._\-]*)?$")

_job = {"thread": None, "name": "", "state": "idle", "status": "", "percent": 0.0,
        "error": "", "cancel": False, "started": 0.0}


class _Cancelled(Exception):
    pass


def _router():
    from ai_control import router
    return router


def _ram_gb():
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) / 1024 / 1024
    except (OSError, ValueError):
        pass
    return 0.0


def _free_disk_gb():
    for candidate in ("/usr/share/ollama", str(Path.home() / ".ollama"), str(Path.home())):
        if Path(candidate).exists():
            return shutil.disk_usage(candidate).free / 1e9
    return 0.0


def _size_gb(name):
    for known, size, _ in RECOMMENDED:
        if known == name:
            return size, True
    match = re.search(r":(\d+(?:\.\d+)?)b\b", name.lower())
    return (float(match.group(1)) * 0.6, False) if match else (0.0, False)


def _ram_needed(size):
    return round(size * 1.3 + 1.5, 1)


def _installed_names():
    try:
        return {m.name for m in _router().installed(refresh=True)}
    except Exception:
        return set()


def _is_installed(name, installed):
    return name in installed or (":" not in name and f"{name}:latest" in installed)


def _list():
    try:
        return "Installed models:\n\n" + _router().describe() + \
               "\n\nGet more with: ollama recommended   |   pick one with: use model <name>"
    except Exception as error:
        return f"Sounix: Could not reach Ollama: {error}\n(Is 'ollama serve' running?)"


def _recommended():
    ram, disk = _ram_gb(), _free_disk_gb()
    try:
        installed = {m.name for m in _router().installed(refresh=True)}
    except Exception as error:
        return f"Sounix: Could not reach Ollama: {error}\n(Is 'ollama serve' running?)"
    lines = ["========== RECOMMENDED MODELS ==========", "",
             f"This computer: {ram:.0f} GB RAM, {disk:.0f} GB free disk for models.", "",
             f"  {'model':<20}{'size':>7}  {'status':<22} good for"]
    for name, size, purpose in RECOMMENDED:
        if _is_installed(name, installed):
            status = "installed"
        elif ram and _ram_needed(size) > ram:
            status = f"needs ~{_ram_needed(size):.0f} GB RAM"
        elif disk and size * 1.2 > disk:
            status = "not enough disk"
        else:
            status = "fits - ollama pull"
        lines.append(f"  {name:<20}{size:>5.1f}GB  {status:<22} {purpose}")
    lines += ["", "Download one with:  ollama pull <name>      (example: ollama pull llama3.1:8b)",
              "Any model on ollama.com/library works too. Sizes shown are approximate."]
    return "\n".join(lines)


def _announce(text):
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", "Sounix: models", text], timeout=5)
        except Exception:
            pass
    try:
        import ai_control
        ai_control.voice_output(f"[ollama] {text}")
    except Exception:
        print(f"[ollama] {text}")


def _progress(status, fraction):
    if _job["cancel"]:
        raise _Cancelled()
    _job["status"] = status
    if fraction:
        _job["percent"] = round(fraction * 100, 1)


def _worker(name):
    try:
        _router().client.pull(name, _progress)
        _router().installed(refresh=True)
        _job.update(state="done", percent=100.0, status="success")
        _announce(f"Model {name} is ready. Use it with: use model {name}")
    except _Cancelled:
        _job.update(state="cancelled")
    except Exception as error:
        message = str(error)
        if "file does not exist" in message or "not found" in message.lower():
            message = f"Ollama has no model called '{name}'. Check the name and tag on ollama.com/library."
        _job.update(state="failed", error=message)
        _announce(f"Download of {name} failed: {message}")


def _running():
    return _job["thread"] is not None and _job["thread"].is_alive()


def _pull(name):
    base, sep, tag = name.strip().partition(":")
    name = base.lower() + sep + tag          # model names are lowercase; tags like q4_K_M are not
    if not NAME_OK.fullmatch(name) or len(name) > 100:
        return ("Sounix: That doesn't look like a model name. Use letters, numbers and - . _ "
                "with an optional :tag, e.g. llama3.1:8b")
    if _running():
        return f"Sounix: Already downloading {_job['name']} ({_job['percent']}%). One at a time. Type: ollama status"
    if _is_installed(name, _installed_names()):
        return f"Sounix: {name} is already installed. Use it with: use model {name}"

    size, known = _size_gb(name)
    ram, disk = _ram_gb(), _free_disk_gb()
    if size and disk and size * 1.2 > disk:
        return (f"Sounix: Not enough free disk. {name} needs about {size:.1f} GB and you have "
                f"{disk:.0f} GB free. Free some space first (df -h).")
    warning = ""
    if size and ram and _ram_needed(size) > ram:
        warning = (f"\nWarning: it may need about {_ram_needed(size):.0f} GB RAM and this computer has "
                   f"{ram:.0f} GB, so it could be very slow or fail to load.")
    _job.update(name=name, state="downloading", status="starting", percent=0.0, error="",
                cancel=False, started=time.time())
    thread = threading.Thread(target=_worker, args=(name,), daemon=True)
    _job["thread"] = thread
    thread.start()
    guess = f" (about {size:.1f} GB{'' if known else ', estimated'})" if size else ""
    return (f"Sounix: Downloading {name}{guess} in the background. You can keep using Sounix.\n"
            f"Check progress with: ollama status   |   stop with: ollama cancel{warning}")


def _status():
    state = _job["state"]
    if state == "idle":
        return "Sounix: No download yet. Try: ollama recommended"
    name = _job["name"]
    if state == "downloading":
        minutes = (time.time() - _job["started"]) / 60
        return f"Sounix: Downloading {name}: {_job['percent']}%  ({_job['status']}, {minutes:.1f} min so far)"
    if state == "done":
        return f"Sounix: {name} finished. Use it with: use model {name}"
    if state == "cancelled":
        return f"Sounix: Download of {name} was cancelled. Pull it again to resume."
    return f"Sounix: Download of {name} failed: {_job['error']}"


def _cancel():
    if not _running():
        return "Sounix: Nothing is downloading."
    _job["cancel"] = True
    return f"Sounix: Stopping the download of {_job['name']}. Pulling it again later resumes where it stopped."


def run(args):
    parts = args.split()
    if not parts or parts[0].lower() == "help":
        return HELP
    action = parts[0].lower()
    if action in {"recommended", "recommend", "browse"} and len(parts) == 1:
        return _recommended()
    if action == "list" and len(parts) == 1:
        return _list()
    if action == "pull" and len(parts) == 2:
        return _pull(parts[1])
    if action == "status" and len(parts) == 1:
        return _status()
    if action == "cancel" and len(parts) == 1:
        return _cancel()
    return "Sounix: Use: ollama recommended | list | pull <name> | status | cancel   (ollama help)"
