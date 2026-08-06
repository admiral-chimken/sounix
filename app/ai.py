from antivirus import scan_path
from firewall import firewall_status, enable_firewall, disable_firewall
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
from natural_commands import normalize_command
from file_manager import (
    list_files,
    make_folder,
    copy_file,
    move_file,
    rename_file,
    delete_file,
)
from settings import settings_report
from tailscale import tailscale_status
from updater import check_updates, update_sounix
import getpass

pending_action = None


def respond(message):
    global pending_action

    original = message.strip()
    command = normalize_command(original)

    if not command:
        return "Sounix: Please enter a command."

    # Handle yes/no answers for actions awaiting confirmation.
    if pending_action is not None:
        if command in {"yes", "y"}:
            action = pending_action
            pending_action = None

            if action == "enable firewall":
                return enable_firewall()

            if action == "disable firewall":
                return disable_firewall()

            if action == "shutdown":
                return shutdown_computer()

            if action == "restart":
                return restart_computer()

            if action.startswith("delete:"):
                path = action.split(":", 1)[1]
                return delete_file(path)

            if action.startswith("install:"):
                package = action.split(":", 1)[1]
                return install_package(package)

            return "Sounix: The pending action was not recognized."

        if command in {"no", "n", "cancel"}:
            pending_action = None
            return "Sounix: Action cancelled."

        return "Sounix: Please answer yes or no."

    # Basic conversation
    if command in {"hello", "hi", "hey"}:
        username = getpass.getuser().capitalize()   
    return (
     f"sounix: hello (username)."
  )  

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

    if command == "enable firewall":
        pending_action = "enable firewall"

        return (
            "Sounix: You are about to enable the firewall.\n\n"
            "A firewall helps block unwanted network connections and is "
            "recommended for most users.\n\n"
            "A terminal will open and request your administrator password.\n"
            "Continue? (yes/no)"
        )

    if command == "disable firewall":
        pending_action = "disable firewall"

        return (
            "Sounix: Warning!\n\n"
            "Disabling your firewall can reduce your computer's security.\n\n"
            "Only continue if you understand why you are doing it.\n\n"
            "A terminal will open and request your administrator password.\n"
            "Continue? (yes/no)"
        )

    if command in {
        "security",
        "dashboard",
        "cyber",
        "cyber center",
        "health",
        "system health",
        "security health",
        "health report",
    }:
        return security_dashboard()

    # System information
    if command in {"system", "system info", "status"}:
        return system_report()

    if command in {"travel", "travel mode"}:
        return travel_report()

    if command == "doctor":
        return doctor()

    if command in {"distro", "distribution", "os"}:
        return get_distro()

    # VPN and Tailscale
    if command in {"vpn", "vpn status"}:
        return vpn_status()

    if command in {"tailscale", "tailscale status"}:
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
        except Exception as error:
            return f"Sounix: I couldn't calculate that: {error}"

    # Package manager
    if command.startswith("install "):
        package = original[8:].strip()

        if not package:
            return "Sounix: Use: install <package>"

        pending_action = f"install:{package}"

        return (
            f"Sounix: You are about to install:\n{package}\n\n"
            "Installing software may require administrator permission and "
            "will download files from your system's package repositories.\n\n"
            "Continue? (yes/no)"
        )

    if command.startswith("search package "):
        query = original[15:].strip()

        if not query:
            return "Sounix: Use: search package <name>"

        return search_packages(query)

    # Power controls
    if command == "shutdown":
        pending_action = "shutdown"

        return (
            "Sounix: You are about to shut down your computer.\n\n"
            "Please save any open work first.\n\n"
            "Continue? (yes/no)"
        )

    if command == "restart":
        pending_action = "restart"

        return (
            "Sounix: You are about to restart your computer.\n\n"
            "Please save any open work first.\n\n"
            "Continue? (yes/no)"
        )

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
            return "Sounix: Use: rename old-path new-name"

        source = parts[0]
        new_name = parts[1]
        return rename_file(source, new_name)

    if command.startswith("delete "):
        path = original[7:].strip()

        if not path:
            return "Sounix: Use: delete <file-or-folder>"

        pending_action = f"delete:{path}"

        return (
            "Sounix: You are about to permanently delete:\n"
            f"{path}\n\n"
            "This action may not be reversible.\n\n"
            "Continue? (yes/no)"
        )

    # Settings and updates
    if command in {"settings", "config"}:
        return settings_report()

    if command == "check updates":
        return check_updates()

    if command == "update sounix":
        return update_sounix()
    if command == "version":
        return (
            "Sounix Version 1.0.0\n\n"
            "Status: Beta\n"
            "Language: Python\n"
            "Platform: Linux\n"
            "Developer: AdmiralChimken\n"
            "GitHub:\n"
            "https://github.com/admiral-chimken/sounix"
        )
    if command == "version":
        return (
            "Sounix Version 1.0.0\n\n"
            "Status: Beta\n"
            "Language: Python\n"
            "Platform: Linux\n"
            "Developer: AdmiralChimken\n"
            "Project:\n"
            "https://github.com/admiral-chimken/sounix"
        )
    if command in {
        "health",
        "system health",
        "health report",
        "security health",
    }:
        return health_report()
    
    if command in {"about", "who are you", "creator"}:
        return (
            "Hello, I'm Sounix.\n\n"
            "I'm a cybersecurity-focused, multipurpose assistant created to "
            "help protect, manage, and better understand your computer.\n\n"
            "I may not be like ChatGPT, Claude, or other AI assistants, "
            "but I have my own purpose.\n\n"
            "I was built using Python, with Arch Linux as my original "
            "development environment.\n\n"
            "I'm still under active development, so new features and "
            "improvements will continue over time.\n\n"
            "Created and developed by AdmiralChimken.\n\n"
            "GitHub:\n"
            "https://github.com/admiral-chimken/sounix\n\n"
            "Thank you for using Sounix!"
        )  
    if command in {"news", "what's new", "whats new", "updates"}:
        return (
            "========== SOUNIX NEWS ==========\n\n"
            "Version: 1.0.0 Beta\n\n"
            "Latest Improvements:\n"
            "• New graphical interface\n"
            "• Firewall safety confirmations\n"
            "• Software installation confirmations\n"
            "• Shutdown and restart confirmations\n"
            "• File delete confirmations\n"
            "• About and Version commands\n"
            "• Improved Arch Linux support\n"
            "• Improved Kali Linux compatibility\n"
            "• Updated installer\n\n"
            "Coming Soon:\n"
            "• Voice interaction\n"
            "• Better natural language understanding\n"
            "• Modern dashboard\n"
            "• Automatic updates\n"
            "• Windows and macOS installers\n\n"
            "Thank you for supporting Sounix!"
        )
    if command == "help security":
        return (
            "========== SECURITY HELP ==========\n\n"
            "firewall status\n"
            "enable firewall\n"
            "disable firewall\n"
            "security\n"
            "health\n"
            "doctor\n"
            "vpn status\n"
            "tailscale status\n"
            "network scan\n"
            "scan <path>\n"
        )

    if command == "help files":
        return (
            "========== FILE HELP ==========\n\n"
            "list <folder>\n"
            "make folder <path>\n"
            "copy source destination\n"
            "move source destination\n"
            "rename old-path new-name\n"
            "delete <file-or-folder>\n"
        )

    if command == "help memory":
        return (
            "========== MEMORY HELP ==========\n\n"
            "remember key = value\n"
            "recall key\n"
            "forget key\n"
            "memories\n"
        )

    if command == "help system":
        return (
            "========== SYSTEM HELP ==========\n\n"
            "system\n"
            "distro\n"
            "settings\n"
            "travel mode\n"
            "shutdown\n"
            "restart\n"
            "sleep\n"
            "lock screen\n"
            "check updates\n"
            "update sounix\n"
        )

    if command in {"help network", "help networking"}:
        return (
            "========== NETWORK HELP ==========\n\n"
            "vpn status\n"
            "tailscale status\n"
            "network scan\n"
            "firewall status\n"
        )

    if command in {"help assistant", "help general"}:
        return (
            "========== ASSISTANT HELP ==========\n\n"
            "hello\n"
            "about\n"
            "who are you\n"
            "creator\n"
            "version\n"
            "news\n"
            "google <search>\n"
            "calculate <expression>\n"
        )
    # Help
    if command in {"help", "commands", "what can you do"}:
        return (
            "========== SOUNIX COMMANDS ==========\n"
            "\n"
            "General:\n"
            "  hello\n"
            "  help\n"
            "\n"
            "About Sounix:\n"
            "  about\n"
            "  who are you\n"
            "  creator\n"
            "  version\n"
            "  news\n"          
            "\n" 
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
            "  tailscale status\n"
            "  network scan\n"
            "\n"
            "System:\n"
            "  system\n"
            "  distro\n"
            "  settings\n"
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
            " health\n"
            "Files:\n"
            "  list <folder>\n"
            "  make folder <path>\n"
            "  copy source destination\n"
            "  move source destination\n"
            "  rename old-path new-name\n"
            "  delete <file-or-folder>\n"
            "Help Categories:\n"
            "  help security\n"
            "  help files\n"
            "  help memory\n"
            "  help system\n"
            "  help network\n"
            "  help assistant\n"
            "\n"
            "Updates:\n"
            "  check updates\n"
            "  update sounix\n"
            "\n"
            "  exit\n"
            "====================================="
        )

    return "Sounix: I do not understand that command yet."
