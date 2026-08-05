import shutil
from pathlib import Path


def expand_path(path):
    return Path(path).expanduser().resolve()


def list_files(path):
    folder = expand_path(path)

    if not folder.exists():
        return f"Sounix: '{folder}' does not exist."

    if not folder.is_dir():
        return f"Sounix: '{folder}' is not a folder."

    items = sorted(folder.iterdir())

    if not items:
        return f"Sounix: '{folder}' is empty."

    lines = [f"Sounix files in {folder}:"]

    for item in items:
        marker = "[Folder]" if item.is_dir() else "[File]"
        lines.append(f"{marker} {item.name}")

    return "\n".join(lines)


def make_folder(path):
    folder = expand_path(path)

    if folder.exists():
        return f"Sounix: '{folder}' already exists."

    try:
        folder.mkdir(parents=True)
        return f"Sounix: Created folder '{folder}'."

    except Exception as error:
        return f"Sounix: Could not create folder: {error}"


def copy_file(source, destination):
    source_path = expand_path(source)
    destination_path = expand_path(destination)

    if not source_path.exists():
        return f"Sounix: '{source_path}' does not exist."

    if not source_path.is_file():
        return "Sounix: The source must be a file."

    answer = input(
        f"Sounix: Copy '{source_path}' to '{destination_path}'? (yes/no): "
    ).strip().lower()

    if answer not in {"yes", "y"}:
        return "Sounix: Copy cancelled."

    try:
        shutil.copy2(source_path, destination_path)
        return f"Sounix: Copied '{source_path}' to '{destination_path}'."

    except Exception as error:
        return f"Sounix: Could not copy the file: {error}"


def move_file(source, destination):
    source_path = expand_path(source)
    destination_path = expand_path(destination)

    if not source_path.exists():
        return f"Sounix: '{source_path}' does not exist."

    answer = input(
        f"Sounix: Move '{source_path}' to '{destination_path}'? (yes/no): "
    ).strip().lower()

    if answer not in {"yes", "y"}:
        return "Sounix: Move cancelled."

    try:
        shutil.move(str(source_path), str(destination_path))
        return f"Sounix: Moved '{source_path}' to '{destination_path}'."

    except Exception as error:
        return f"Sounix: Could not move the file: {error}"
