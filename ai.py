import shutil
from antivirus import scan_path
from firewall import firewall_status
from system_info import system_report
from memory import remember, recall, forget, list_memories
from calculator import calculate
from google import google_search
from security_dashboard import security_dashboard
from travel_mode import travel_report
from vpn_check import vpn_status
from software_manager import install_package, search_packages
from doctor import doctor
from network_scan import network_scan
from power_control import (
    shutdown_computer,
    restart_computer,
    sleep_computer,
    lock_screen,
)
from distro import get_distro
from admin_tools import enable_firewall, disable_firewall 
from natural_commands import normalize_command

def respond(message):
    original = message.strip()
    command = normalize_command(original)
    if command.startswith("google "):
        query = original[7:].strip()
        return google_search(query)
    if command in ("security", "dashboard"):
       return security_dashboard()
    if command in ("vpn", "vpn status"):
       return vpn_status()
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
        target = original[5:].strip()
        return scan_path(target)

    if command in {"firewall", "firewall status"}:
        return firewall_status()

    if command == "system":
        return system_report()

    if command.startswith("remember "):
        parts = original.split(" ", 2)

        if len(parts) < 3:
            return "Sounix: Use: remember key value"

        key = parts[1].lower()
        value = parts[2]
        remember(key, value)
        return f"Sounix: I remembered {key}."

    if command.startswith("recall "):
        key = original[7:].strip().lower()
        answer = recall(key)

        if answer is None:
            return "Sounix: I do not remember that yet."

        return f"Sounix: {answer}"

    if command == "memories":
        saved = list_memories()

        if not saved:
            return "Sounix: I do not have any memories yet."

        lines = ["Sounix memories:"]
        for key, value in saved.items():
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    if command.startswith("forget "):
        key = original[7:].strip().lower()
        forget(key)
        return f"Sounix: I forgot {key}."
    if command.startswith("calculate "):
        expression = original[10:].strip()

        try:
            answer = calculate(expression)
            return f"Sounix: {answer}"
        except Exception:
            return "Sounix: I couldn't calculate that."
    if command.startswith("install"):
        package = original[8:].strip ()
        return install_package(package)
    if command.startswith("search package "):
       query = original [15:]. strip()
       return search_packages(query)
    if command in ("travel", "travel mode"):
         return travel_report()
    if command == "doctor":
       return doctor()
    if command == "network scan":
        return network_scan()
    if command == "shutdown":
        return shutdown_computer()

    if command == "restart":
        return restart_computer()

    if command == "sleep":
        return sleep_computer()
    if command in ("distro", "distribution", "os"):
       return get_distro()
    if command in {"lock", "lock screen"}:
        return lock_screen()
    if command == "enable firewall":
       return enable_firewall()
    if command == "disable firewall":
       return disable_firewall()
    if command == "help":
       return (
       
           "Commands:\n"
            "  hello\n"
            "  status\n"
            "  scan ~/Downloads\n"
            "  scan ~/sounix\n"
            "  firewall status\n"
            "  system\n"
            "  secuirty\n"
            "  google\n"
            "  dashboard\n"
            "  remember key value\n"
            "  recall key\n"
            "  distro\n" 
            "  memories\n"
            "  travel/n"   
            "  forget key\n"
            "  vpn\n"
            "  vpn status\n"
            "  network scan\n"
            "  install firefox\n"
            " search package firefox\n"
            "  help\n"
            "  doctor\n"
            "  shutdown\n"
            "  restart\n"
            "  sleep\n"
            "  lock screen\n"
            "  exit"
        )

    return "Sounix: I do not understand that command yet."
