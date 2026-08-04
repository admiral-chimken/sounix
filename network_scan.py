import ipaddress
import subprocess


def get_local_network():
    result = subprocess.run(
        ["ip", "-4", "route", "show", "default"],
        capture_output=True,
        text=True,
        timeout=5,
    )

    words = result.stdout.split()

    if "src" not in words:
        return None

    ip_address = words[words.index("src") + 1]
    network = ipaddress.ip_network(f"{ip_address}/24", strict=False)

    return str(network)


def network_scan():
    network = get_local_network()

    if network is None:
        return "Sounix: I could not determine the local network."

    try:
        result = subprocess.run(
            ["nmap", "-sn", network],
            capture_output=True,
            text=True,
            timeout=90,
        )

        if result.returncode != 0:
            error = result.stderr.strip()
            return f"Sounix: Network scan failed: {error}"

        return (
            f"Sounix: Scanning devices on {network}\n\n"
            + result.stdout.strip()
        )

    except FileNotFoundError:
        return "Sounix: Nmap is not installed."

    except subprocess.TimeoutExpired:
        return "Sounix: The network scan took too long."

