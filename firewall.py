import shutil
import subprocess


def firewall_status():
    if shutil.which("ufw") is None:
        return (
            "Sounix: UFW is not installed.\n"
            "Install it with: sudo pacman -S ufw"
        )

    try:
        result = subprocess.run(
            ["sudo", "-n", "ufw", "status", "verbose"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "Sounix: The firewall check timed out."
    except OSError as error:
        return f"Sounix: Firewall check failed: {error}"

    if result.returncode == 0:
        return "Sounix firewall report:\n" + result.stdout.strip()

    return (
        "Sounix: Administrator permission is required.\n"
        "Run this in the terminal:\n"
        "sudo ufw status verbose"
    )
