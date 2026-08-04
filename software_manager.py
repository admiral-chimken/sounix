import re
import shutil
import subprocess


PACKAGE_PATTERN = re.compile(r"^[a-zA-Z0-9@._+-]+$")


def valid_package_name(package):
    return bool(PACKAGE_PATTERN.fullmatch(package))


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
        result = subprocess.run(
            ["pacman", "-Ss", query],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.stdout.strip():
            return result.stdout.strip()

        return "Sounix: No matching packages found."

    except Exception as error:
        return f"Sounix: Search error: {error}"
