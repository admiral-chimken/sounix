import os
import shutil
import subprocess


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        return result.stdout.strip()

    except Exception:
        return ""


def get_wifi_name():
    # Windows
    if os.name == "nt":
        output = run_command(
            [
                "netsh",
                "wlan",
                "show",
                "interfaces",
            ]
        )

        for line in output.splitlines():
            line = line.strip()

            if line.lower().startswith("ssid") and not line.lower().startswith(
                "bssid"
            ):
                parts = line.split(":", 1)

                if len(parts) == 2:
                    return parts[1].strip()

        return "Not connected"

    # Linux
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
    # Windows
    if os.name == "nt":
        output = run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-NetFirewallProfile | "
                    "Select-Object -ExpandProperty Enabled"
                ),
            ]
        )

        if not output:
            return "Unknown"

        states = [
            line.strip().lower()
            for line in output.splitlines()
            if line.strip()
        ]

        if states and all(state == "true" for state in states):
            return "Active"

        if "true" in states:
            return "Partially active"

        return "Inactive"

    # Linux - UFW
    if shutil.which("ufw"):
        output = run_command(
            ["ufw", "status"]
        )

        if "Status: active" in output:
            return "Active"

        return "Inactive"

    # Linux - firewalld
    if shutil.which("firewall-cmd"):
        output = run_command(
            ["firewall-cmd", "--state"]
        )

        if output == "running":
            return "Active"

        return "Inactive"

    return "No supported firewall found"


def get_open_ports():
    # Windows
    if os.name == "nt":
        output = run_command(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "Get-NetTCPConnection -State Listen "
                    "| Select-Object -ExpandProperty LocalPort"
                ),
            ]
        )

        ports = {
            line.strip()
            for line in output.splitlines()
            if line.strip().isdigit()
        }

        if not ports:
            return "No listening TCP ports found"

        return f"{len(ports)} listening TCP ports"

    # Linux
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
        "public_wifi",
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
            "Your firewall does not appear fully active."
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
            f"- {warning}"
            for warning in warnings
        )

    return (
        "========== SOUNIX TRAVEL MODE ==========\n\n"
        f"Wi-Fi: {wifi}\n"
        f"Firewall: {firewall}\n"
        f"Ports: {ports}\n"
        f"Risk level: {risk}\n\n"
        f"Advice:\n{advice}\n\n"
        "- Use HTTPS websites.\n"
        "- Turn off file sharing on networks you do not trust.\n"
        "- Use a trusted VPN on public Wi-Fi."
    )
