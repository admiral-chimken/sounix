import os
import re
import shutil
import subprocess


PACKAGE_PATTERN = re.compile(r"^[a-zA-Z0-9@._+-]+$")
SEARCH_PATTERN = re.compile(r"^[a-zA-Z0-9@._+\- ]+$")


def valid_package_name(package):
    return bool(PACKAGE_PATTERN.fullmatch(package))


def valid_search(query):
    return bool(SEARCH_PATTERN.fullmatch(query))


def get_package_manager():
    # Windows
    if os.name == "nt" and shutil.which("winget"):
        return "winget"

    # Linux
    if shutil.which("pacman"):
        return "pacman"

    if shutil.which("apt"):
        return "apt"

    if shutil.which("dnf"):
        return "dnf"

    return None


def install_package(package):
    package = package.strip()

    if not valid_package_name(package):
        return "Sounix: That package name contains invalid characters."

    package_manager = get_package_manager()

    if package_manager == "pacman":
        command = [
            "sudo",
            "pacman",
            "-S",
            "--needed",
            "--noconfirm",
            package,
        ]

    elif package_manager == "apt":
        command = [
            "sudo",
            "apt",
            "install",
            "-y",
            package,
        ]

    elif package_manager == "dnf":
        command = [
            "sudo",
            "dnf",
            "install",
            "-y",
            package,
        ]

    elif package_manager == "winget":
        command = [
            "winget",
            "install",
            package,
            "--accept-package-agreements",
            "--accept-source-agreements",
        ]

    else:
        return (
            "Sounix: No supported package manager was found.\n\n"
            "Supported package managers:\n"
            "pacman - Arch Linux\n"
            "apt - Debian, Ubuntu, Kali\n"
            "dnf - Fedora\n"
            "winget - Windows"
        )

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )

        if result.returncode == 0:
            return (
                f"Sounix: {package} was installed successfully."
            )

        error = result.stderr.strip()

        if not error:
            error = result.stdout.strip()

        return (
            "Sounix: Installation failed.\n\n"
            f"{error}"
        )

    except subprocess.TimeoutExpired:
        return "Sounix: The installation timed out."

    except OSError as error:
        return f"Sounix: Installation error: {error}"


def search_packages(query):
    query = query.strip()

    if not query:
        return "Sounix: Enter a package to search for."

    if not valid_search(query):
        return "Sounix: That search contains invalid characters."

    package_manager = get_package_manager()

    if package_manager == "pacman":
        command = [
            "pacman",
            "-Ss",
            query,
        ]

    elif package_manager == "apt":
        command = [
            "apt",
            "search",
            query,
        ]

    elif package_manager == "dnf":
        command = [
            "dnf",
            "search",
            query,
        ]

    elif package_manager == "winget":
        command = [
            "winget",
            "search",
            query,
        ]

    else:
        return "Sounix: No supported package manager was found."

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

        output = result.stdout.strip()

        if output:
            return output

        error = result.stderr.strip()

        if error:
            return (
                "Sounix: Package search failed.\n\n"
                f"{error}"
            )

        return "Sounix: No matching packages found."

    except subprocess.TimeoutExpired:
        return "Sounix: Package search timed out."

    except OSError as error:
        return f"Sounix: Search error: {error}"
