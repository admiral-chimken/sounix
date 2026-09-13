"""
threat_detection.py
------------------------
Feature #1 for Sounix: Advanced Threat Detection, scoped realistically.

Cross-platform (Windows/Mac/Linux) using psutil instead of shelling
out to OS-specific commands like 'ss' or 'ps'.

No machine learning -- this is straightforward anomaly detection:
save a "baseline" snapshot of open ports and running processes, then
later compare a fresh snapshot against that baseline and flag
anything new that wasn't there before.
"""

import psutil

from memory import remember, recall


def get_open_ports():
    """
    Returns a set of strings describing currently listening ports,
    using psutil (works the same way on Windows, Mac, and Linux).
    """
    try:
        ports = set()
        for conn in psutil.net_connections(kind="inet"):
            if conn.status == psutil.CONN_LISTEN and conn.laddr:
                ports.add(f"{conn.laddr.ip}:{conn.laddr.port}")
        return ports
    except (psutil.AccessDenied, PermissionError):
        # On some OSes, listing all connections needs admin/root rights.
        return set()
    except Exception:
        return set()


def get_running_processes():
    """
    Returns a set of currently running process names, using psutil.
    """
    try:
        names = set()
        for proc in psutil.process_iter(["name"]):
            name = proc.info.get("name")
            if name:
                names.add(name)
        return names
    except Exception:
        return set()


def set_baseline():
    ports = get_open_ports()
    processes = get_running_processes()

    remember("baseline_ports", list(ports))
    remember("baseline_processes", list(processes))

    return (
        f"Sounix: Baseline saved. "
        f"{len(ports)} open port(s), {len(processes)} running process(es) recorded."
    )


def scan_for_threats():
    baseline_ports = recall("baseline_ports")
    baseline_processes = recall("baseline_processes")

    if baseline_ports is None or baseline_processes is None:
        return "Sounix: No baseline set yet. Run 'Set Baseline' first."

    current_ports = get_open_ports()
    current_processes = get_running_processes()

    new_ports = current_ports - set(baseline_ports)
    new_processes = current_processes - set(baseline_processes)

    if not new_ports and not new_processes:
        return "Sounix: No new ports or processes detected since baseline. Looks normal."

    lines = ["Sounix: Changes detected since baseline:"]

    if new_ports:
        lines.append(f"\nNew open port(s) ({len(new_ports)}):")
        for p in sorted(new_ports):
            lines.append(f"  - {p}")

    if new_processes:
        lines.append(f"\nNew running process(es) ({len(new_processes)}):")
        for p in sorted(new_processes):
            lines.append(f"  - {p}")

    lines.append(
        "\nNote: new items aren't automatically malicious -- this just "
        "flags what's different from your baseline. Review anything "
        "unfamiliar."
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print(set_baseline())
    print(scan_for_threats())
