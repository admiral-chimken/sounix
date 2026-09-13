import os
import platform
import shutil
import psutil
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
    report.append(f"Disk Used: {round(used / (1024**3))} GB")
    report.append(f"Disk Free: {round(free / (1024**3))} GB")
    report.append(f"Disk Total: {round(total / (1024**3))} GB")
    report.append("")

    mem = psutil.virtual_memory()
    report.append(f"RAM Used: {round(mem.used / (1024**3), 1)} GB")
    report.append(f"RAM Available: {round(mem.available / (1024**3), 1)} GB")
    report.append(f"RAM Total: {round(mem.total / (1024**3), 1)} GB")

    return "\n".join(report)
