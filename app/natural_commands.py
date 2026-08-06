def normalize_command(command):
    command = command.strip().lower()

    exact_commands = {
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

        "check vpn": "vpn status",
        "check my vpn": "vpn status",
        "is my vpn connected": "vpn status",

        "scan network": "network scan",
        "scan my network": "network scan",

        "check system": "doctor",
        "check my system": "doctor",
        "run system check": "doctor",

        "what linux am i using": "distro",
        "what distro am i using": "distro",
        "detect linux": "distro",

        "turn on firewall": "enable firewall",
        "start firewall": "enable firewall",

        "turn off firewall": "disable firewall",
        "stop firewall": "disable firewall",
    }

    if command in exact_commands:
        return exact_commands[command]

    if command.startswith("install package "):
        package = command[16:].strip()
        return f"install {package}"

    if command.startswith("find package "):
        package = command[13:].strip()
        return f"search package {package}"

    return command
