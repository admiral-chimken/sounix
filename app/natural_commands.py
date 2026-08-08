def normalize_command(command):
    command = command.strip().lower()

    exact_commands = {
        # Power
        "turn off computer": "shutdown",
        "turn off the computer": "shutdown",
        "shut down computer": "shutdown",
        "shut down the computer": "shutdown",

        "reboot computer": "restart",
        "reboot the computer": "restart",
        "restart computer": "restart",
        "restart the computer": "restart",

        "put computer to sleep": "sleep",
        "put the computer to sleep": "sleep",

        "lock computer": "lock screen",
        "lock the computer": "lock screen",

        # VPN
        "check vpn": "vpn status",
        "check my vpn": "vpn status",
        "is my vpn connected": "vpn status",
        "is vpn connected": "vpn status",
        "show vpn status": "vpn status",

        # Network
        "scan network": "network scan",
        "scan my network": "network scan",
        "check network": "network scan",
        "check my network": "network scan",

        # System
        "check system": "doctor",
        "check my system": "doctor",
        "run system check": "doctor",
        "how is my computer": "doctor",
        "how is my system": "doctor",

        "show system info": "system",
        "show my system info": "system",
        "system information": "system",

        "what linux am i using": "distro",
        "what distro am i using": "distro",
        "detect linux": "distro",
        "what operating system am i using": "distro",

        # Firewall
        "turn on firewall": "enable firewall",
        "start firewall": "enable firewall",
        "enable my firewall": "enable firewall",

        "turn off firewall": "disable firewall",
        "stop firewall": "disable firewall",
        "disable my firewall": "disable firewall",

        "check firewall": "firewall status",
        "check my firewall": "firewall status",
        "is my firewall on": "firewall status",
        "is my firewall enabled": "firewall status",
        "show firewall status": "firewall status",

        # Security
        "check security": "security",
        "check my security": "security",
        "security status": "security",
        "run health check": "health",
        "check health": "health",

        # Updates
        "check for updates": "check updates",
        "are there updates": "check updates",
        "is sounix up to date": "check updates",

        "update sounix now": "update sounix",
        "install sounix update": "update sounix",

        # Assistant
        "who are you": "about",
        "tell me about yourself": "about",
        "introduce yourself": "about",

        "what version are you": "version",
        "show version": "version",

        "what's new": "news",
        "whats new": "news",
        "show news": "news",
    }

    if command in exact_commands:
        return exact_commands[command]

    if command.startswith("install package "):
        package = command[16:].strip()
        return f"install {package}"

    if command.startswith("find package "):
        package = command[13:].strip()
        return f"search package {package}"

    if command.startswith("search for "):
        query = command[11:].strip()
        return f"google {query}"

    if command.startswith("look up "):
        query = command[8:].strip()
        return f"google {query}"

    return command
