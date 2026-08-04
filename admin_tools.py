import subprocess


def run_admin_command(command, success_message, failure_message):
    answer = input(
        f"Sounix: Run {' '.join(command)}? (yes/no): "
    ).strip().lower()

    if answer not in {"yes", "y"}:
        return "Sounix: Admin action cancelled."

    result = subprocess.run(command)

    if result.returncode == 0:
        return success_message

    return failure_message


def enable_firewall():
    return run_admin_command(
        ["sudo", "ufw", "enable"],
        "Sounix: Firewall enabled.",
        "Sounix: Could not enable the firewall.",
    )


def disable_firewall():
    return run_admin_command(
        ["sudo", "ufw", "disable"],
        "Sounix: Firewall disabled.",
        "Sounix: Could not disable the firewall.",
    )
