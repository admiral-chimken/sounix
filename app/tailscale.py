import shutil
import subprocess


def tailscale_status():
    if not shutil.which("tailscale"):
        return "Sounix: Tailscale is not installed."

    try:
        result = subprocess.run(
            ["tailscale", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return "Sounix: Tailscale did not respond."

    output = (result.stdout or result.stderr).strip()
    return output or "Sounix: Tailscale returned no status."
