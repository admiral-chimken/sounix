import nmap

def run_scan(target, arguments="-sV"):
    scanner = nmap.PortScanner()
    try:
        scanner.scan(target, arguments=arguments)
    except Exception as e:
        return f"Scan failed: {str(e)}"

    hosts = scanner.all_hosts()
    if not hosts:
        return f"No results for {target}. Host may be unreachable."

    host = hosts[0]  # use the actual scanned host key (may be resolved IP)
    output = [f"Scan results for {target} ({host}):"]
    host_info = scanner[host]
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
