import subprocess


def confirm_action(action):
    answer = input(
        f"Sounix: Are you sure you want to {action}? (yes/no): "
    ).strip().lower()

    return answer in {"yes", "y"}


def shutdown_computer():
    if not confirm_action("shut down the computer"):
        return "Sounix: Shutdown cancelled."

    result = subprocess.run(["systemctl", "poweroff"])

    if result.returncode == 0:
        return "Sounix: Shutting down."

    return "Sounix: Shutdown failed."


def restart_computer():
    if not confirm_action("restart the computer"):
        return "Sounix: Restart cancelled."

    result = subprocess.run(["systemctl", "reboot"])

    if result.returncode == 0:
        return "Sounix: Restarting."

    return "Sounix: Restart failed."


def sleep_computer():
    if not confirm_action("put the computer to sleep"):
        return "Sounix: Sleep cancelled."

    result = subprocess.run(["systemctl", "suspend"])

    if result.returncode == 0:
        return "Sounix: Entering sleep mode."

    return "Sounix: Sleep failed."


def lock_screen():
    commands = [
        ["loginctl", "lock-session"],
        ["xdg-screensaver", "lock"],
    ]

    for command in commands:
        try:
            result = subprocess.run(command)

            if result.returncode == 0:
                return "Sounix: Screen locked."
        except FileNotFoundError:
            continue

    return "Sounix: I could not lock the screen."
