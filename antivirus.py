import shutil
import subprocess
from pathlib import Path


def scan_path(target="~"):
    path = Path(target).expanduser().resolve()

    if not path.exists():
        return f"Sounix: I cannot find {path}"

    if shutil.which("clamscan") is None:
        return "Sounix: ClamAV is not installed."

    command = ["clamscan", "--infected"]

    if path.is_dir():
        command.append("--recursive")

    command.append(str(path))

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "Sounix: The antivirus scan timed out."
    except OSError as error:
        return f"Sounix: ClamAV could not start: {error}"

    output = result.stdout.strip()

    if result.returncode == 0:
        return f"Sounix: Scan completed. No threats found.\n\n{output}"

    if result.returncode == 1:
        return f"Sounix: WARNING! A possible threat was found.\n\n{output}"

    details = result.stderr.strip() or output
    return f"Sounix: The scan failed.\n{details}"
