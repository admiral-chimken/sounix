"""Sounix Spotify plugin: control the Spotify desktop app through playerctl.

  spotify                 what is playing now
  spotify pause | play | toggle | next | previous
  spotify volume <0-100>
"""
import shutil
import subprocess

COMMAND = "spotify"

HELP = (
    "========== SPOTIFY HELP ==========\n\n"
    "spotify                  show what is playing\n"
    "spotify pause            pause\n"
    "spotify play             play / resume\n"
    "spotify toggle           pause or play\n"
    "spotify next             next track\n"
    "spotify previous         previous track\n"
    "spotify volume <0-100>   set volume\n"
    "pause spotify            same as: spotify pause\n\n"
    "Needs the Spotify desktop app and:  sudo apt install playerctl"
)

ACTIONS = {
    "pause": (["pause"], "Paused Spotify."),
    "play": (["play"], "Playing Spotify."),
    "resume": (["play"], "Playing Spotify."),
    "toggle": (["play-pause"], "Toggled Spotify."),
    "next": (["next"], "Skipped to the next track."),
    "skip": (["next"], "Skipped to the next track."),
    "previous": (["previous"], "Went back a track."),
    "back": (["previous"], "Went back a track."),
}


def _playerctl(*args):
    return subprocess.run(["playerctl", *args], capture_output=True, text=True, timeout=5)


def run(args):
    if not shutil.which("playerctl"):
        return "Sounix: playerctl is not installed. Run: sudo apt install playerctl"

    words = args.lower().split()
    action = words[0] if words else "now"
    if action == "help":
        return HELP

    try:
        names = _playerctl("-l").stdout.split()
        if not any(name.startswith("spotify") for name in names):
            others = f" (other players: {', '.join(names)})" if names else ""
            return "Sounix: Spotify is not running." + others

        if action in ACTIONS:
            command, message = ACTIONS[action]
            result = _playerctl("-p", "spotify", *command)
            return f"Sounix: {message}" if result.returncode == 0 else f"Sounix: Spotify error: {result.stderr.strip()}"

        if action in {"now", "status", "playing"}:
            status = _playerctl("-p", "spotify", "status").stdout.strip() or "Unknown"
            track = _playerctl("-p", "spotify", "metadata", "--format", "{{artist}} - {{title}}").stdout.strip()
            return f"Sounix: Spotify is {status.lower()}." + (f"\n{track}" if track else "")

        if action == "volume":
            if len(words) != 2 or not words[1].isdigit() or not 0 <= int(words[1]) <= 100:
                return "Sounix: Use: spotify volume <0-100>"
            result = _playerctl("-p", "spotify", "volume", f"{int(words[1]) / 100:.2f}")
            return f"Sounix: Volume set to {words[1]}%." if result.returncode == 0 else f"Sounix: Spotify error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Sounix: Spotify did not respond."

    return "Sounix: Use: spotify pause | play | next | previous | volume <0-100>   (spotify help)"
