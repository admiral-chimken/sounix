import shutil
import socket
import subprocess


def get_command_output(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "Unavailable"


def network_status():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "Connected"
    except OSError:
        return "Disconnected"


def security_dashboard():
    clamav = (
        "Installed"
        if shutil.which("clamscan")
        else "Not installed"
    )

    firewall = (
        "Available"
        if shutil.which("ufw")
        else "Not installed"
    )

    disk = get_command_output(
        ["df", "-h", "/"]
    )

    memory = get_command_output(
        ["free", "-h"]
    )

    uptime = get_command_output(
        ["uptime", "-p"]
    )

    network = network_status()

    return (
        "=== Sounix Security Dashboard ===\n"
        f"ClamAV: {clamav}\n"
        f"Firewall tools: {firewall}\n"
        f"Network: {network}\n"
        f"Uptime: {uptime}\n\n"
        f"Disk usage:\n{disk}\n\n"
        f"Memory usage:\n{memory}"
    )
