import shutil
from antivirus import scan_path
from firewall import firewall_status
from system_info import system_report

def respond(message):
    original = message.strip()
    command = original.lower()

    if command in {"hello", "hi", "hey"}:
        return "Sounix: Hello, William. I am online."

    if command == "status":
        clamav = "available" if shutil.which("clamscan") else "not installed"
        ufw = "available" if shutil.which("ufw") else "not installed"

        return (
            "Sounix status:\n"
            "Core: online\n"
            f"ClamAV: {clamav}\n"
            f"Firewall tools: {ufw}"
        )

    if command == "scan":
        return scan_path("~")

    if command.startswith("scan "):
        target = command[5:].strip()
        return scan_path(target)

    if command in {"firewall", "firewall status"}:
        return firewall_status()
   
    if command == "system":
        return system_report()

    if command == "help":
        return (
            "Commands:\n"
            "  hello\n"
            "  status\n"
            "  scan ~/Downloads\n"
            "  scan ~/sounix\n"
            "  firewall status\n"
            "  help\n"
            " system/n"
            "  exit"
        )

    return "Sounix: I do not understand that command yet."
