import shlex
import shutil
import subprocess


def _install_instruction():
    """Return the correct UFW installation command for this system."""
    if shutil.which("pacman"):
        return "sudo pacman -S ufw"

    if shutil.which("apt") or shutil.which("apt-get"):
        return "sudo apt install ufw"

    if shutil.which("dnf"):
        return "sudo dnf install ufw"

    return "Install the 'ufw' package using your system package manager."


def _ufw_missing_message():
    return (
        "Sounix: UFW (Uncomplicated Firewall) is not installed.\n\n"
        "A firewall helps protect your computer by blocking unwanted "
        "network connections.\n\n"
        "To install it:\n"
        f"  {_install_instruction()}\n\n"
        "After installation, run:\n"
        "  firewall status"
    )


def _find_terminal():
    """Find a supported graphical terminal emulator."""
    terminals = (
        "gnome-terminal",
        "konsole",
        "kitty",
        "alacritty",
        "foot",
        "x-terminal-emulator",
        "xterm",
    )

    for terminal in terminals:
        if shutil.which(terminal):
            return terminal

    return None


def _open_admin_terminal(ufw_arguments, action_name):
    """
    Open a terminal so sudo can safely request the user's password.

    Sounix never reads or stores the password.
    """
    terminal = _find_terminal()

    if terminal is None:
        command = "sudo ufw " + " ".join(
            shlex.quote(argument) for argument in ufw_arguments
        )

        return (
            "Sounix: Administrator permission is required, but no supported "
            "terminal emulator was found.\n"
            f"Run this manually:\n{command}"
        )

    command = ["sudo", "ufw", *ufw_arguments]
    displayed_command = shlex.join(command)

    script = (
        f"{displayed_command}; "
        "result=$?; "
        "echo; "
        f"echo 'Sounix: {action_name} finished with exit code' $result; "
        "echo; "
        "read -r -p 'Press Enter to close this window...'; "
        "exit $result"
    )

    try:
        if terminal == "gnome-terminal":
            subprocess.Popen(
                [terminal, "--", "bash", "-lc", script],
                start_new_session=True,
            )

        elif terminal == "konsole":
            subprocess.Popen(
                [terminal, "-e", "bash", "-lc", script],
                start_new_session=True,
            )

        else:
            subprocess.Popen(
                [terminal, "-e", "bash", "-lc", script],
                start_new_session=True,
            )

    except OSError as error:
        return f"Sounix: Could not open the administrator terminal: {error}"

    return (
        "Sounix: Opening a terminal for administrator permission.\n"
        "Enter your system password there to continue."
    )


def firewall_status():
    """Show UFW status, requesting administrator permission when needed."""
    if shutil.which("ufw") is None:
        return _ufw_missing_message()

    try:
        result = subprocess.run(
            ["sudo", "-n", "ufw", "status", "verbose"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    except subprocess.TimeoutExpired:
        return "Sounix: The firewall status check timed out."

    except OSError as error:
        return f"Sounix: Firewall status check failed: {error}"

    if result.returncode == 0:
        report = result.stdout.strip()

        if not report:
            report = "No firewall status information was returned."

        return f"Sounix firewall report:\n{report}"

    return _open_admin_terminal(
        ["status", "verbose"],
        "firewall status check",
    )


def enable_firewall():
    if shutil.which("ufw") is None:
        return _ufw_missing_message()

    return _open_admin_terminal(
        ["--force", "enable"],
        "firewall enable command",
    )


def disable_firewall():
    if shutil.which("ufw") is None:
        return _ufw_missing_message()

    return _open_admin_terminal(
        ["disable"],
        "firewall disable command",
    )
