import platform


def get_distro():
    system = platform.system()

    if system == "Windows":
        return (
            f"Sounix: Windows {platform.release()} detected."
        )

    if system == "Darwin":
        return (
            f"Sounix: macOS {platform.mac_ver()[0]} detected."
        )

    if system != "Linux":
        return f"Sounix: {system} detected."

    try:
        with open("/etc/os-release", "r") as file:
            data = file.read().lower()

        if "id=arch" in data:
            return "Sounix: Arch Linux detected."

        if "id=kali" in data:
            return "Sounix: Kali Linux detected."

        if "id=ubuntu" in data:
            return "Sounix: Ubuntu detected."

        if "id=debian" in data:
            return "Sounix: Debian detected."

        if "id=fedora" in data:
            return "Sounix: Fedora detected."

        if "id=opensuse" in data or "id=suse" in data:
            return "Sounix: openSUSE detected."

        return "Sounix: Unknown Linux distribution."

    except OSError:
        return "Sounix: Unable to determine Linux distribution."
