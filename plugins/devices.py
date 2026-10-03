"""Sounix devices plugin: list and check YOUR devices (local network + Tailscale).

Read-only. Only private and Tailscale addresses can be checked.
  devices                  list Tailscale machines and local-network devices
  devices check <name|ip>  ping the device and list its common open ports
  devices trust            remember every device on this network as yours
  devices new              show devices that are NOT on your trusted list
  devices known            show the trusted list for this network
  devices watch on [min]   re-scan in the background and alert on new devices
  devices watch off | status
  devices help
"""
import ipaddress
import json
import re
import shutil
import subprocess
import threading
from datetime import datetime
from pathlib import Path

COMMAND = "devices"

TAILSCALE_NET = ipaddress.ip_network("100.64.0.0/10")

HELP = (
    "========== DEVICES HELP ==========\n\n"
    "devices                   list Tailscale machines and local-network devices\n"
    "devices check <name|ip>   ping a device and list its common open ports\n"
    "devices trust             remember every device on this network as yours\n"
    "devices new               show devices that are not on your trusted list\n"
    "devices known             show the trusted list for this network\n"
    "devices watch on [min]    re-scan in the background (default every 10 min) and alert\n"
    "devices watch off | status\n\n"
    "Run 'devices trust' only when you recognize every device on the list.\n"
    "Trusted lists are kept per network, so travelling doesn't cause false alarms.\n"
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


# ---- trusted devices and alerts ------------------------------------
def _state_dir():
    return Path.home() / ".sounix"


def _load_known():
    try:
        data = json.loads((_state_dir() / "known_devices.json").read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_known(known):
    _state_dir().mkdir(parents=True, exist_ok=True)
    (_state_dir() / "known_devices.json").write_text(json.dumps(known, indent=2))


def _is_known(dev, entries):
    """Both sides have a MAC: compare MACs. Otherwise fall back to the IP address."""
    for entry in entries:
        if dev["mac"] and entry.get("mac"):
            if dev["mac"].lower() == entry["mac"].lower():
                return True
        elif dev["ip"] == entry.get("ip"):
            return True
    return False


def _unknown(devices, entries):
    return [dev for dev in devices if not _is_known(dev, entries)]


def _line(dev):
    return f"{dev['ip']:<16} {dev['name'] or '(no name)':<24} {dev['mac']}".rstrip()


def _trust():
    network, devices, note = _lan_devices()
    if not devices:
        return f"Sounix: Nothing was saved. {note or 'No devices answered the scan.'}"
    known = _load_known()
    entries = known.get(network, [])
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    added = 0
    for dev in devices:
        if not _is_known(dev, entries):
            entries.append({"ip": dev["ip"], "name": dev["name"], "mac": dev["mac"], "added": stamp})
            added += 1
    known[network] = entries
    _save_known(known)
    lines = [f"Sounix: Trusted {len(devices)} devices on {network} ({added} new to the list):", ""]
    lines += [f"  {_line(dev)}" for dev in devices]
    lines += ["", "If any of these is not yours, don't use this list. Check your router first."]
    return "\n".join(lines)


def _new():
    network, devices, note = _lan_devices()
    if not devices:
        return f"Sounix: {note or 'No devices answered the scan.'}"
    entries = _load_known().get(network)
    if not entries:
        return (f"Sounix: You have no trusted list for {network} yet.\n"
                "Run 'devices trust' while you recognize every device on the network.")
    strangers = _unknown(devices, entries)
    if not strangers:
        return f"Sounix: All {len(devices)} devices on {network} are on your trusted list."
    lines = [f"Sounix: {len(strangers)} device(s) on {network} are NOT on your trusted list:", ""]
    lines += [f"  {_line(dev)}" for dev in strangers]
    lines += ["", "If one is yours (a new phone, say), run 'devices trust' to add it."]
    return "\n".join(lines)


def _known():
    network, _, note = _lan_devices()
    if not network:
        return f"Sounix: {note}"
    entries = _load_known().get(network, [])
    if not entries:
        return f"Sounix: No trusted list for {network}. Run 'devices trust'."
    lines = [f"Trusted devices on {network}:", ""]
    lines += [f"  {entry['ip']:<16} {entry.get('name') or '(no name)':<24} {entry.get('mac', '')}".rstrip()
              for entry in entries]
    return "\n".join(lines)


_watch = {"thread": None, "stop": None, "minutes": 10, "alerts": 0, "alerted": set()}


def _alert(text):
    _watch["alerts"] += 1
    try:
        _state_dir().mkdir(parents=True, exist_ok=True)
        with open(_state_dir() / "device_alerts.log", "a") as handle:
            handle.write(f"{datetime.now().isoformat(timespec='seconds')}  {text}\n")
    except OSError:
        pass
    if shutil.which("notify-send"):
        try:
            subprocess.run(["notify-send", "-u", "critical", "Sounix: new device on your network", text],
                           timeout=5)
        except Exception:
            pass
    message = f"[devices] New device on your network: {text}"
    try:
        import ai_control
        ai_control.voice_output(message)
    except Exception:
        print(message)


def _watch_loop(stop, minutes):
    while not stop.is_set():
        try:
            network, devices, _ = _lan_devices()
            entries = _load_known().get(network or "")
            if entries and devices:
                for dev in _unknown(devices, entries):
                    key = (dev["mac"] or dev["ip"]).lower()
                    if key not in _watch["alerted"]:
                        _watch["alerted"].add(key)
                        _alert(_line(dev))
        except Exception:
            pass
        stop.wait(minutes * 60)


def _watch_command(parts):
    action = parts[0].lower() if parts else "status"
    running = _watch["thread"] is not None and _watch["thread"].is_alive()
    if action == "on":
        if running:
            return f"Sounix: Already watching (every {_watch['minutes']} minutes)."
        minutes = 10
        if len(parts) > 1:
            if not parts[1].isdigit() or not 2 <= int(parts[1]) <= 1440:
                return "Sounix: Use: devices watch on [minutes]   (2 to 1440)"
            minutes = int(parts[1])
        stop = threading.Event()
        thread = threading.Thread(target=_watch_loop, args=(stop, minutes), daemon=True)
        _watch.update(thread=thread, stop=stop, minutes=minutes)
        thread.start()
        return (f"Sounix: Watching your network every {minutes} minutes. New devices will pop up\n"
                "here and as a desktop notification. It only alerts on networks where you ran\n"
                "'devices trust', and it stops when you close Sounix.")
    if action == "off":
        if not running:
            return "Sounix: Not watching."
        _watch["stop"].set()
        return "Sounix: Stopped watching."
    if action == "status":
        if not running:
            return "Sounix: Not watching. Start with: devices watch on"
        return f"Sounix: Watching every {_watch['minutes']} minutes. Alerts so far: {_watch['alerts']}."
    return "Sounix: Use: devices watch on [minutes] | off | status"


def run(args):
    parts = args.split()
    if not parts:
        return _list()
    action = parts[0].lower()
    if action == "help":
        return HELP
    if action == "check" and len(parts) == 2:
        return _check(parts[1])
    if action == "trust" and len(parts) == 1:
        return _trust()
    if action == "new" and len(parts) == 1:
        return _new()
    if action == "known" and len(parts) == 1:
        return _known()
    if action == "watch":
        return _watch_command(parts[1:])
    return "Sounix: Use: devices   or   devices check <name or ip>\n(type 'devices help' for details)"
