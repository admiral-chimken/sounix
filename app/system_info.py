import os
import platform
import shutil
from pathlib import Path


def system_report():
    total, used, free = shutil.disk_usage(Path.home())

    report = []

    report.append("===== Sounix System Information =====")
    report.append(f"User: {os.getenv('USER')}")
    report.append(f"Computer: {platform.node()}")
    report.append(f"Operating System: {platform.system()}")
    report.append(f"Release: {platform.release()}")
    report.append(f"Architecture: {platform.machine()}")
    report.append(f"Python Version: {platform.python_version()}")
    report.append("")
    report.append(f"Disk Used: {used // (1024**3)} GB")
    report.append(f"Disk Free: {free // (1024**3)} GB")
    report.append(f"Disk Total: {total // (1024**3)} GB")

    return "\n".join(report)
