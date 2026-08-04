import re
import shutil
import subprocess


PACKAGE_PATTERN = re.compile(r"^[a-zA-Z0-9@._+-]+$")


def valid_package_name(package):
    return bool(PACKAGE_PATTERN.fullmatch(package))

def get_package_manager():
    if shutil.which("pacman"):
        return "pacman"

    if shutil.which("apt"):
        return "apt"

        package_manager = get_package_manager()

    if package_manager == "pacman":
        command = ["sudo", "pacman", "-S", "--needed", package]

    elif package_manager == "apt":
        command = ["sudo", "apt", "install", "-y", package]

    elif package_manager == "dnf":
        command = ["sudo", "dnf", "install", "-y", package]

    else:
        return "Sounix: No supported package manager was found."

def install_package(package):
    package = package.strip()

    if not valid_package_name(package):
        return "Sounix: That package name contains invalid characters."

    if not shutil.which("pacman"):
        return "Sounix: Pacman was not found."

    command = ["sudo", "pacman", "-S", "--needed", package]

    print(f"Sounix: I am ready to run: {' '.join(command)}")
    confirmation = input("Sounix: Continue? (yes/no): ").strip().lower()

    if confirmation not in {"yes", "y"}:
        return "Sounix: Installation cancelled."

    try:
        result = subprocess.run(command)

        if result.returncode == 0:
            return f"Sounix: {package} was installed successfully."

        return f"Sounix: Installation failed with code {result.returncode}."

    except Exception as error:
        return f"Sounix: Installation error: {error}"


def search_packages(query):
    query = query.strip()

    if not valid_package_name(query):
        return "Sounix: That search contains invalid characters."

    try:
        package_manager = get_package_manager()

        if package_manager == "pacman":
            command = ["pacman", "-Ss", query]

        elif package_manager == "apt":
            command = ["apt", "search", query]

        elif package_manager == "dnf":
            command = ["dnf", "search", query]

        else:
            return "Sounix: No supported package manager was found."

        result = subprocess.run(
            command,
           
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout.strip():
            return result.stdout.strip()

        return "Sounix: No matching packages found."

    except Exception as error:
        return f"Sounix: Search error: {error}"
