import shutil
import subprocess


def firewall_status():
    if shutil.which("ufw") is None:
        return (
            "Sounix: UFW is not installed.\n"
            "Install it with: sudo pacman -S ufw"
        )

    result = subprocess.run(
        ["ufw", "status", "verbose"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        return "Sounix firewall report:\n" + result.stdout.strip()

    return "Sounix: Unable to read firewall status."


def enable_firewall():
    if shutil.which("ufw") is None:
        return "Sounix: UFW is not installed."

    result = subprocess.run(
        ["sudo", "ufw", "enable"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return "Sounix: Firewall enabled successfully."

    return (
        "Sounix: Firewall enable failed.\n"
        + result.stderr.strip()
    )


def disable_firewall():
    if shutil.which("ufw") is None:
        return "Sounix: UFW is not installed."

    result = subprocess.run(
        ["sudo", "ufw", "disable"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return "Sounix: Firewall disabled successfully."

    return (
        "Sounix: Firewall disable failed.\n"
        + result.stderr.strip()
    )
