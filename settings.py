import platform 
import shutil 

from firewall import firewall_status 
from vpn_check import vpn_status
from distro import get_distro

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
    return( 
          "========== SOUNIX SETTINGS ==========\n"
          f"versioon: (sounix_version)\n"
          f"system: (platform.system())\n"
          f"machine: (platform.machine())\n"
          f"distro: (get-distro())\n" 
          f"package manager(get_package_manager())\n"
          "\n"
          f"firewall:\n(firewall_status())\n"
           "====================================="
    )         
