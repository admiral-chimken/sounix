import platform


def get_os():
    system = platform.system()

    if system == "Linux":
        return "Linux"

    elif system == "Windows":
        return "Windows"

    elif system == "Darwin":
        return "macOS"

    else:
        return system


def get_os_details():
    return (
        "========== SYSTEM ==========\n"
        f"Operating System: {get_os()}\n"
        f"Machine: {platform.machine()}\n"
        f"Processor: {platform.processor()}\n"
        "============================"
    )
