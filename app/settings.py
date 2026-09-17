import platform 
import shutil 

from firewall import firewall_status 
from vpn_check import vpn_status
from distro import get_distro
from os_detect import get_os_details
sounix_version = "1.0 Beta"

def get_package_manager():
    if shutil.which("pacman"):
        return "pacman (Arch Linux)"
    if shutil.which ("apt"):
        return "apt (Debian/Kali)"

    if shutil.which ("dnf"):
        return "dnf (fedora)"

    if shutil.which("zypper"):
        return "zypper (openSUSE)"

    return "unknown" 


def settings_report():
    return (
        "========== SOUNIX SETTINGS ==========\n"
        f"Version: {sounix_version}\n"
        f"System: {platform.system()}\n"
        f"Machine: {platform.machine()}\n"
        f"Distro: {get_distro()}\n"
        f"Package Manager: {get_package_manager()}\n"
        "\n"
        f"Firewall:\n{firewall_status()}\n"
        f"{get_os_details()}\n"
        "====================================="
    )         
