"""Sounix plugin: 'pause', 'pause spotify', 'pause music', 'pause all'."""
import shutil
import subprocess

COMMAND = "pause"


def run(args):
    if not shutil.which("playerctl"):
        return "Sounix: playerctl is not installed. Run: sudo apt install playerctl"

    target = args.lower().strip()
    if target in {"", "spotify", "music"}:
        command, label = ["-p", "spotify", "pause"], "Spotify"
    elif target == "all":
        command, label = ["-a", "pause"], "all players"
    else:
        return "Sounix: Use: pause   |   pause spotify   |   pause all"

    try:
        names = subprocess.run(["playerctl", "-l"], capture_output=True, text=True, timeout=5).stdout.split()
        if label == "Spotify" and not any(name.startswith("spotify") for name in names):
            others = f" (other players: {', '.join(names)})" if names else ""
            return "Sounix: Spotify is not running." + others
        result = subprocess.run(["playerctl", *command], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return "Sounix: The player did not respond."

    if result.returncode != 0:
        return f"Sounix: Could not pause: {result.stderr.strip() or 'no player found'}"
    return f"Sounix: Paused {label}."
