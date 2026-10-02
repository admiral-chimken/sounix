"""Sounix devices plugin: list and check YOUR devices (local network + Tailscale).

Read-only. Only private and Tailscale addresses can be checked.
  devices                  list Tailscale machines and local-network devices
  devices check <name|ip>  ping the device and list its common open ports
  devices help
"""
import ipaddress
import json
import re
import shutil
import subprocess

COMMAND = "devices"

TAILSCALE_NET = ipaddress.ip_network("100.64.0.0/10")

HELP = (
    "========== DEVICES HELP ==========\n\n"
    "devices                   list Tailscale machines and local-network devices\n"
    "devices check <name|ip>   ping a device and list its common open ports\n\n"
    "Only your own private (192.168.x.x, 10.x.x.x) and Tailscale addresses can be checked.\n"
    "A Tailscale machine can be checked by name, e.g.  devices check raspberrypi"
)


def _run(cmd, timeout):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _tailscale_nodes():
    """Returns (nodes, note). Each node: name, ip, os, online, me."""
    if not shutil.which("tailscale"):
        return [], "Tailscale is not installed."
    try:
        result = _run(["tailscale", "status", "--json"], 10)
        data = json.loads(result.stdout)
    except subprocess.TimeoutExpired:
        return [], "Tailscale did not respond."
    except ValueError:
        return [], "Tailscale is not running or not logged in."
    entries = [(data.get("Self") or {}, True)]
    entries += [(peer, False) for peer in (data.get("Peer") or {}).values()]
    nodes = []
    for node, is_me in entries:
        if not node:
            continue
        ips = [ip for ip in node.get("TailscaleIPs", []) if "." in ip]
        nodes.append({
            "name": node.get("HostName", "?"),
            "ip": ips[0] if ips else "",
            "os": node.get("OS", ""),
            "online": bool(node.get("Online", is_me)),
            "me": is_me,
        })
    return nodes, ""


def _neighbors():
    """IP -> MAC for devices this computer has recently talked to."""
    try:
        result = _run(["ip", "neigh", "show"], 5)
    except Exception:
        return {}
    found = {}
    for line in result.stdout.splitlines():
        match = re.match(r"(\d+\.\d+\.\d+\.\d+) .*lladdr ([0-9a-fA-F:]{17})", line)
        if match:
            found[match.group(1)] = match.group(2)
    return found


def _lan_devices():
    """Returns (network, devices, note)."""
    try:
        from network_scan import get_local_network
        network = get_local_network()
    except Exception as error:
        return None, [], f"Could not determine the local network ({error})."
    if network is None:
        return None, [], "Could not determine the local network."
    try:
        result = _run(["nmap", "-sn", "-oG", "-", network], 90)
    except FileNotFoundError:
        return network, [], "nmap is not installed (sudo apt install nmap)."
    except subprocess.TimeoutExpired:
        return network, [], "The scan took too long."
    macs = _neighbors()
    devices = []
    for line in result.stdout.splitlines():
        match = re.match(r"Host: (\S+) \((.*?)\)\s+Status: Up", line)
        if match:
            devices.append({
                "ip": match.group(1),
                "name": match.group(2),
                "mac": macs.get(match.group(1), ""),
            })
    return network, devices, ""


def _list():
    lines = ["========== SOUNIX DEVICES ==========", "", "Tailscale:"]
    nodes, note = _tailscale_nodes()
    if nodes:
        for node in nodes:
            state = "this computer" if node["me"] else ("online" if node["online"] else "offline")
            lines.append(f"  {node['name']:<18} {node['ip']:<16} {node['os']:<9} {state}")
    else:
        lines.append(f"  {note or 'No devices.'}")

    network, devices, note = _lan_devices()
    lines += ["", f"Local network ({network or 'unknown'}):"]
    if devices:
        for dev in devices:
            lines.append(f"  {dev['ip']:<16} {dev['name'] or '(no name)':<24} {dev['mac']}")
    else:
        lines.append(f"  {note or 'No devices answered.'}")
    lines += ["", "Check one with:  devices check <name or ip>"]
    return "\n".join(lines)


def _resolve(target):
    """Returns (ip, label). Raises ValueError unless it is a private or Tailscale address."""
    try:
        ip = ipaddress.ip_address(target)
        label = target
    except ValueError:
        nodes, _ = _tailscale_nodes()
        wanted = target.lower()
        usable = [n for n in nodes if n["ip"]]
        matches = ([n for n in usable if n["name"].lower() == wanted]
                   or [n for n in usable if n["name"].lower().startswith(wanted)])
        if len(matches) != 1:
            raise ValueError(f"I don't know a device called '{target}'. Type 'devices' to see the list.")
        ip, label = ipaddress.ip_address(matches[0]["ip"]), matches[0]["name"]
    if ip.version != 4 or not (ip.is_private or ip in TAILSCALE_NET):
        raise ValueError("For safety I only check private (home network) and Tailscale addresses.")
    return ip, label


def _check(target):
    try:
        ip, label = _resolve(target)
    except ValueError as error:
        return f"Sounix: {error}"

    lines = [f"========== DEVICE CHECK: {label} ({ip}) ==========", ""]

    try:
        result = _run(["ping", "-c", "2", "-W", "2", str(ip)], 15)
        latency = re.search(r"= [\d.]+/([\d.]+)/", result.stdout)
        text = "reachable" if result.returncode == 0 else "no reply to ping"
        if latency:
            text += f" ({latency.group(1)} ms average)"
        lines.append(f"Ping:  {text}")
    except FileNotFoundError:
        lines.append("Ping:  ping is not installed")
    except subprocess.TimeoutExpired:
        lines.append("Ping:  timed out")

    try:
        result = _run(["nmap", "-F", "-Pn", "--open", str(ip)], 90)
        ports = re.findall(r"^(\d+/(?:tcp|udp))\s+open\s+(\S+)", result.stdout, re.M)
        if ports:
            lines.append("Open ports (top 100 checked):")
            lines += [f"  {port:<10} {service}" for port, service in ports]
        else:
            lines.append("Open ports: none found among the 100 most common.")
    except FileNotFoundError:
        lines.append("Ports: nmap is not installed (sudo apt install nmap)")
    except subprocess.TimeoutExpired:
        lines.append("Ports: the scan took too long")

    lines += ["", "Open ports can be normal. Close any service you don't use."]
    return "\n".join(lines)


def run(args):
    parts = args.split()
    if not parts:
        return _list()
    action = parts[0].lower()
    if action == "help":
        return HELP
    if action == "check" and len(parts) == 2:
        return _check(parts[1])
    return "Sounix: Use: devices   or   devices check <name or ip>\n(type 'devices help' for details)"
