import os
import subprocess


def get_network_interfaces():
    try:
        if os.name == "nt":
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        "Get-NetAdapter | "
                        "Where-Object {$_.Status -eq 'Up'} | "
                        "Select-Object -ExpandProperty Name"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            return result.stdout.lower()

        result = subprocess.run(
            ["ip", "-brief", "address"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )

        return result.stdout.lower()

    except Exception:
        return ""


def vpn_status():
    interfaces = get_network_interfaces()

    if not interfaces:
        return "Sounix: I could not read the network interfaces."

    # Tailscale
    if "tailscale" in interfaces:
        return "Sounix: Tailscale VPN detected."

    # WireGuard
    if "wireguard" in interfaces or "wg0" in interfaces:
        return "Sounix: WireGuard VPN detected."

    # OpenVPN / tunnel adapters
    if (
        "tun0" in interfaces
        or "tap" in interfaces
        or "openvpn" in interfaces
    ):
        return "Sounix: OpenVPN-style connection detected."

    # Proton VPN
    if "proton" in interfaces:
        return "Sounix: Proton VPN detected."

    # Common Windows VPN adapter wording
    if os.name == "nt":
        if "vpn" in interfaces:
            return "Sounix: A Windows VPN adapter is active."

    return "Sounix: No supported VPN connection was detected."
