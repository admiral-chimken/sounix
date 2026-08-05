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
from file_manager import (
    list_files,
    make_folder,
    copy_file,
    move_file,
)
from settings import settings_report
from tailscale import tailscale_status
def respond(message):
    original = message.strip()
    command = normalize_command(original)

    if not command:
        return "Sounix: Please enter a command."

    # Basic conversation
    if command in {"hello", "hi", "hey"}:
        return "Sounix: Hello, William."

    # Google search
    if command.startswith("google "):
        query = original[7:].strip()

        if not query:
            return "Sounix: Tell me what you want to search for."

        return google_search(query)

    # Antivirus
    if command.startswith("scan "):
        path = original[5:].strip()

        if not path:
            return "Sounix: Use: scan <path>"

        return scan_path(path)

    # Firewall and security
    if command in {"firewall", "firewall status"}:
        return firewall_status()

    if command in {"security", "dashboard", "cyber", "cyber center"}:
        return security_dashboard()

    if command == "enable firewall":
        return enable_firewall()

    if command == "disable firewall":
        return disable_firewall()

    # System information
    if command in {"system", "system info", "status"}:
        return system_report()

    if command in {"travel", "travel mode"}:
        return travel_report()

    if command == "doctor":
        return doctor()

    if command in {"distro", "distribution", "os"}:
        return get_distro()

    # VPN
    if command in {"vpn", "vpn status"}:
        return vpn_status()
    # TAILSCALE
    if command in ("tailscale", "tailscale status"):
        return tailscale_status()
    # Network
    if command == "network scan":
        return network_scan()

    # Memory
    if command.startswith("remember "):
        content = original[9:].strip()

        if "=" not in content:
            return "Sounix: Use: remember key = value"

        key, value = content.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        if not key or not value:
            return "Sounix: Use: remember key = value"

        remember(key, value)
        return f"Sounix: I remembered {key}."

    if command.startswith("recall "):
        key = original[7:].strip().lower()

        if not key:
            return "Sounix: Use: recall <key>"

        result = recall(key)

        if result is None:
            return f"Sounix: I do not remember {key}."

        return f"Sounix: {key} = {result}"

    if command.startswith("forget "):
        key = original[7:].strip().lower()

        if not key:
            return "Sounix: Use: forget <key>"

        forget(key)
        return f"Sounix: I forgot {key}."

    if command in {"memory", "memories", "list memories"}:
        return list_memories()

    # Calculator
    if command.startswith("calculate "):
        expression = original[10:].strip()

        if not expression:
            return "Sounix: Use: calculate <expression>"

        try:
            answer = calculate(expression)
            return f"Sounix: {answer}"

        except Exception:
            return "Sounix: I couldn't calculate that."

    # Package manager
    if command.startswith("install "):
        package = original[8:].strip()

        if not package:
            return "Sounix: Use: install <package>"

        return install_package(package)

    if command.startswith("search package "):
        query = original[15:].strip()

        if not query:
            return "Sounix: Use: search package <name>"

        return search_packages(query)

    # Power controls
    if command == "shutdown":
        return shutdown_computer()

    if command == "restart":
        return restart_computer()

    if command == "sleep":
        return sleep_computer()

    if command in {"lock", "lock screen"}:
        return lock_screen()

    # File manager
    if command.startswith("make folder "):
        folder = original[12:].strip()

        if not folder:
            return "Sounix: Use: make folder <path>"

        return make_folder(folder)

    if command.startswith("list "):
        folder = original[5:].strip()

        if not folder:
            return "Sounix: Use: list <folder>"

        return list_files(folder)

    if command.startswith("copy "):
        parts = original[5:].split(maxsplit=1)

        if len(parts) != 2:
            return "Sounix: Use: copy source destination"

        source = parts[0]
        destination = parts[1]
        return copy_file(source, destination)

    if command.startswith("move "):
        parts = original[5:].split(maxsplit=1)

        if len(parts) != 2:
            return "Sounix: Use: move source destination"

        source = parts[0]
        destination = parts[1]
        return move_file(source, destination)

    if command.startswith("rename "):
        parts = original[7:].split(maxsplit=1)

        if len(parts) != 2:
            return "Sounix: Use: rename oldname newname"

        source = parts[0]
        new_name = parts[1]

        return rename_file(source, new_name)
    if command.startswith("delete "):
        path = original[7:].strip()

        if not path:
            return "Sounix: Use: delete <file>"

        return delete_file(path)
    if command in ("settings", "config"):
        return settings_report()
    # Help
    if command in {"help", "commands", "what can you do"}:
        return (
            "========== SOUNIX COMMANDS ==========\n"
            "\n"
            "General:\n"
            "  hello\n"
            "  help\n"
            "  google <search>\n"
            "  calculate <expression>\n"
            "\n"
            "Security:\n"
            "  scan <path>\n"
            "  firewall status\n"
            "  enable firewall\n"
            "  disable firewall\n"
            "  security\n"
            "  doctor\n"
            "  vpn status\n"
            "  network scan\n"
            "\n"
            "System:\n"
            "  system\n"
            "  distro\n"
            "  travel mode\n"
            "  shutdown\n"
            "  restart\n"
            "  sleep\n"
            "  lock screen\n"
            "\n"
            "Memory:\n"
            "  remember key = value\n"
            "  recall key\n"
            "  forget key\n"
            "  memories\n"
            "\n"
            "Software:\n"
            "  install <package>\n"
            "  search package <name>\n"
            "\n"
            "Files:\n"
            "  list <folder>\n"
            "  make folder <path>\n"
            "  copy source destination\n"
            "  move source destination\n"
            "\n"
            "  exit\n"
            "====================================="
        )

    return "Sounix: I do not understand that command yet."   

