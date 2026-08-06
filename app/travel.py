import shutil
import subprocess


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_wifi_name():
    if not shutil.which("nmcli"):
        return "Unknown"

    output = run_command(
        [
            "nmcli",
            "-t",
            "-f",
            "active,ssid",
            "dev",
            "wifi",
        ]
    )

    for line in output.splitlines():
        if line.startswith("yes:"):
            return line.split(":", 1)[1]

    return "Not connected"


def get_firewall_status():
    if shutil.which("ufw"):
        output = run_command(["ufw", "status"])

        if "Status: active" in output:
            return "Active"

        return "Inactive"

    if shutil.which("firewall-cmd"):
        output = run_command(
            ["firewall-cmd", "--state"]
        )

        if output == "running":
            return "Active"

        return "Inactive"

    return "No supported firewall found"


def get_open_ports():
    if not shutil.which("ss"):
        return "Unavailable"

    output = run_command(
        ["ss", "-lntu"]
    )

    lines = output.splitlines()

    if len(lines) <= 1:
        return "No listening ports found"

    return f"{len(lines) - 1} listening network entries"


def travel_report():
    wifi = get_wifi_name()
    firewall = get_firewall_status()
    ports = get_open_ports()

    warnings = []

    suspicious_names = {
        "free wifi",
        "free_wifi",
        "public wifi",
        "guest",
        "airport",
        "hotel",
    }

    if wifi.lower() in suspicious_names:
        warnings.append(
            "This network name looks public."
        )

    if firewall != "Active":
        warnings.append(
            "Your firewall does not appear active."
        )

    if not warnings:
        risk = "Low"
        advice = (
            "No obvious problems were detected. "
            "Still avoid sensitive activity on networks you do not trust."
        )
    else:
        risk = "Medium"
        advice = "\n".join(
            f"- {warning}" for warning in warnings
        )

    return (
        "=== Sounix Travel Mode ===\n"
        f"Wi-Fi: {wifi}\n"
        f"Firewall: {firewall}\n"
        f"Ports: {ports}\n"
        f"Risk level: {risk}\n\n"
        f"Advice:\n{advice}\n"
        "- Use HTTPS websites.\n"
        "- Turn off file sharing.\n"
        "- Avoid unknown USB devices.\n"
        "- Use a trusted VPN on public Wi-Fi."
    )
