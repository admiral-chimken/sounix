"""Sounix plugin: 'play' controls Spotify (via playerctl)."""
import shutil
import subprocess

COMMAND = "play"
ACTION = "play"
MESSAGE = "Playing Spotify."
ALLOWED = {"", "spotify", "music", "song", "track"}


def run(args):
    if not shutil.which("playerctl"):
        return "Sounix: playerctl is not installed. Run: sudo apt install playerctl"

    if args.lower().strip() not in ALLOWED:
        return "Sounix: Use: play   |   play song   |   play spotify"

    try:
        names = subprocess.run(["playerctl", "-l"], capture_output=True, text=True, timeout=5).stdout.split()
        if not any(name.startswith("spotify") for name in names):
            others = f" (other players: {', '.join(names)})" if names else ""
            return "Sounix: Spotify is not running." + others
        result = subprocess.run(["playerctl", "-p", "spotify", ACTION], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        return "Sounix: Spotify did not respond."

    if result.returncode != 0:
        return f"Sounix: Spotify error: {result.stderr.strip() or 'no response'}"
    return "Sounix: " + MESSAGE
