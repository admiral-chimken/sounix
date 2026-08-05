import subprocess
from version import SOUNIX_VERSION


def check_updates():

    try:
        result = subprocess.run(
            ["git", "fetch"],
            capture_output=True,
            text=True,
        )

        status = subprocess.run(
            ["git", "status"],
            capture_output=True,
            text=True,
        )

        if "behind" in status.stdout:
            return (
                "Sounix update available.\n"
                "Run: update sounix"
            )

        return (
            f"Sounix version {SOUNIX_VERSION}\n"
            "Sounix is up to date."
        )

    except Exception as error:
        return f"Sounix update error: {error}"


def update_sounix():

    try:
        subprocess.run(
            ["git", "pull"],
            check=True,
        )

        return "Sounix updated successfully."

    except Exception as error:
        return f"Sounix update failed: {error}"
