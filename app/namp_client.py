import nmap

def run_scan(target, arguments="-sV"):
    """
    Run an nmap scan against a target.
    target: IP address or hostname (e.g. "192.168.1.1" or "scanme.nmap.org")
    arguments: nmap flags as a string (default: -sV for service/version detection)
    """
    scanner = nmap.PortScanner()
    try:
        scanner.scan(target, arguments=arguments)
    except Exception as e:
        return f"Scan failed: {str(e)}"

    if target not in scanner.all_hosts():
        return f"No results for {target}. Host may be down or unreachable."

    output = [f"Scan results for {target}:"]
    host_info = scanner[target]
    output.append(f"State: {host_info.state()}")

    for proto in host_info.all_protocols():
        output.append(f"\nProtocol: {proto}")
        ports = host_info[proto].keys()
        for port in sorted(ports):
            port_info = host_info[proto][port]
            output.append(
                f"  Port {port}: {port_info['state']} "
                f"({port_info.get('name', 'unknown')} "
                f"{port_info.get('product', '')} {port_info.get('version', '')})"
            )

    return "\n".join(output)
