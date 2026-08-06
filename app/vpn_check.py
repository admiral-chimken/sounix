import subprocess



def get_network_interfaces() :

    try:

        result = subprocess.run(

           ["ip", "-brief", "address"],
              
           capture_output=True,
           text=True,
           timeout=5,
      )

        return result.stdout.lower()
    except Exception:

        return ""



def vpn_status():
    interface = get_network_interfaces()

    if "tailscale0" in interface:
       
        return "sounix: tailscale VPN detected on tailscale0"

    if "wg0" in interface:

        return "sounix: Wireguard VPN detected on wg0"

    if "tun0" in interface: 
        
        return "sounix: openVPN-style connection dected on tun0"


    if "proton" in interface:
        
        return "Sounix: Proton VPN detected."
         
 
    return "sounix: No tailscale, wireguard, or tun0 vpn seen."

