import subprocess
from pathlib import Path

from version import SOUNIX_VERSION


PROJECT_DIR = Path(__file__).resolve().parent.parent


def _run_git(*arguments):
    return subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def _is_git_install():
    return (PROJECT_DIR / ".git").is_dir()


def _has_local_changes():
    result = _run_git("status", "--porcelain")

    if result.returncode != 0:
        return False

    return bool(result.stdout.strip())


def check_updates():
    if not _is_git_install():
        return (
            f"Sounix version {SOUNIX_VERSION}\n\n"
            "This copy was installed from a packaged release, so Git-based "
            "updates are unavailable.\n\n"
            "Download the newest release here:\n"
            "https://github.com/admiral-chimken/sounix/releases"
        )

    try:
        fetch_result = _run_git("fetch", "--prune")

        if fetch_result.returncode != 0:
            error = fetch_result.stderr.strip() or fetch_result.stdout.strip()

            return (
                "Sounix: I could not check for updates.\n\n"
                f"Git error:\n{error}"
            )

        upstream_result = _run_git(
            "rev-parse",
            "--abbrev-ref",
            "--symbolic-full-name",
            "@{u}",
        )

        if upstream_result.returncode != 0:
            return (
                "Sounix: This Git branch does not have an upstream branch.\n\n"
                "Run this manually from the Sounix folder:\n"
                "git branch --set-upstream-to=origin/main main"
            )

        count_result = _run_git(
            "rev-list",
            "--count",
            "HEAD..@{u}",
        )

        if count_result.returncode != 0:
            error = count_result.stderr.strip() or count_result.stdout.strip()

            return (
                "Sounix: I could not compare local and online versions.\n\n"
                f"Git error:\n{error}"
            )

        commits_behind = int(count_result.stdout.strip() or "0")

        if commits_behind > 0:
            return (
                f"Sounix version {SOUNIX_VERSION}\n\n"
                f"An update is available with {commits_behind} new "
                f"commit{'s' if commits_behind != 1 else ''}.\n\n"
                "Type:\n"
                "update sounix"
            )

        return (
            f"Sounix version {SOUNIX_VERSION}\n\n"
            "Sounix is up to date."
        )

    except subprocess.TimeoutExpired:
        return "Sounix: The update check timed out."

    except (OSError, ValueError) as error:
        return f"Sounix update error: {error}"


def update_sounix():
    if not _is_git_install():
        return (
            "Sounix: Automatic Git updates are unavailable for packaged "
            "release copies.\n\n"
            "Download the newest release here:\n"
            "https://github.com/admiral-chimken/sounix/releases"
        )

    if _has_local_changes():
        return (
            "Sounix: Update cancelled because this installation has local "
            "code changes.\n\n"
            "Save or discard those changes before updating.\n\n"
            "Check them with:\n"
            "git status"
        )

    try:
        pull_result = _run_git("pull", "--ff-only")

        if pull_result.returncode != 0:
            error = pull_result.stderr.strip() or pull_result.stdout.strip()

            return (
                "Sounix update failed.\n\n"
                f"Git error:\n{error}"
            )

        message = pull_result.stdout.strip()

        if "Already up to date" in message:
            return (
                f"Sounix version {SOUNIX_VERSION}\n\n"
                "Sounix is already up to date."
            )

        return (
            "Sounix updated successfully.\n\n"
            "Close and reopen Sounix to load the new version."
        )

    except subprocess.TimeoutExpired:
        return "Sounix: The update operation timed out."

    except OSError as error:
        return f"Sounix update failed: {error}"
