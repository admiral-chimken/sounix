def get_distro():
    try:
        with open("/etc/os-release", "r") as file:
            data = file.read()

        if "ID=arch" in data:
            return "Sounix: Arch Linux detected."

        elif "ID=kali" in data:
            return "Sounix: Kali Linux detected."

        elif "ID=ubuntu" in data:
            return "Sounix: Ubuntu detected."

        elif "ID=fedora" in data:
            return "Sounix: Fedora detected."

        else:
            return "Sounix: Unknown Linux distribution."

    except Exception:
        return "Sounix: Unable to determine Linux distribution." 
             
    

    
