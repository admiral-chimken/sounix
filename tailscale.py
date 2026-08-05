import subprocess

def tailscale_status():
    result = subprocess.run(
        ["tailscale", "status"],
        capture_output=True,
        text=True
    )

    return result.stdout
