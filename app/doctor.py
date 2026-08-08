import os
import shutil


def check(program):
    return shutil.which(program) is not None


def doctor():
    report = []

    report.append("========== SOUNIX DOCTOR ==========")

    # Python
    if os.name == "nt":
        report.append(
            "✓ Python"
            if check("python") or check("py")
            else "✗ Python"
        )
    else:
        report.append(
            "✓ Python 3"
            if check("python3")
            else "✗ Python 3"
        )

    # Git
    report.append(
        "✓ Git"
        if check("git")
        else "✗ Git"
    )

    # Antivirus
    if os.name == "nt":
        report.append(
            "✓ Windows Security available"
            if check("powershell")
            else "✗ Windows Security check unavailable"
        )
    else:
        report.append(
            "✓ ClamAV"
            if check("clamscan") or check("clamd")
            else "✗ ClamAV"
        )

    # Firewall
    if os.name == "nt":
        report.append(
            "✓ Windows Firewall available"
            if check("powershell")
            else "✗ Windows Firewall check unavailable"
        )
    else:
        report.append(
            "✓ Firewall (UFW)"
            if check("ufw")
            else "✗ Firewall (UFW)"
        )

    # WireGuard
    report.append(
        "✓ WireGuard"
        if check("wg") or check("wireguard")
        else "✗ WireGuard"
    )

    # Nmap
    report.append(
        "✓ Nmap"
        if check("nmap")
        else "✗ Nmap"
    )

    # tcpdump
    if os.name != "nt":
        report.append(
            "✓ tcpdump"
            if check("tcpdump")
            else "✗ tcpdump"
        )

    # Wireshark
    report.append(
        "✓ Wireshark"
        if check("wireshark")
        else "✗ Wireshark"
    )

    # Windows package manager
    if os.name == "nt":
        report.append(
            "✓ winget"
            if check("winget")
            else "✗ winget"
        )

    report.append("===================================")

    return "\n".join(report)
