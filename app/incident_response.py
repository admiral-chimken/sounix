"""
incident_response.py
------------------------
Feature #5 for Sounix: basic evidence collection + a guided response
checklist for when something suspicious is found.

Evidence collection is NOT full forensics (no disk imaging, no memory
dumps) -- it's a practical snapshot: processes, network connections,
and recent auth log entries, saved to a timestamped file you can keep
or share.
"""

import subprocess
from datetime import datetime

import psutil

from ollama_client import ask_ollama

EVIDENCE_DIR = "incident_reports"


def _get_recent_auth_log(lines=30):
    try:
        result = subprocess.run(
            ["tail", "-n", str(lines), "/var/log/auth.log"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "(could not read auth log -- may need elevated permissions)"
    except Exception as e:
        return f"(error reading auth log: {e})"


def collect_evidence():
    import os
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{EVIDENCE_DIR}/incident_{timestamp}.txt"

    lines = []
    lines.append(f"===== Sounix Incident Report =====")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")

    lines.append("--- Running Processes ---")
    try:
        for proc in psutil.process_iter(["pid", "name", "username"]):
            info = proc.info
            lines.append(f"  PID {info['pid']}: {info['name']} (user: {info['username']})")
    except Exception as e:
        lines.append(f"  (error collecting processes: {e})")

    lines.append("")
    lines.append("--- Network Connections ---")
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr:
                raddr = f" -> {conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
                lines.append(f"  {conn.laddr.ip}:{conn.laddr.port}{raddr} [{conn.status}]")
    except Exception as e:
        lines.append(f"  (error collecting connections: {e})")

    lines.append("")
    lines.append("--- Recent Auth Log (last 30 lines) ---")
    lines.append(_get_recent_auth_log())

    report_text = "\n".join(lines)

    with open(filename, "w") as f:
        f.write(report_text)

    return f"Sounix: Evidence collected and saved to {filename}"


def incident_checklist(situation):
    if not situation or not situation.strip():
        return "Sounix: Use: incident checklist <describe what you found>"

    prompt = (
        f"I found this on my system and I'm concerned it might be a "
        f"security incident: {situation}\n\n"
        "Give me a clear, numbered step-by-step response checklist. "
        "Include: how to verify if it's actually a threat, how to "
        "contain it safely, and what NOT to do (avoid destroying "
        "evidence). Keep it practical for a home/personal Linux "
        "machine, not an enterprise environment."
    )

    return ask_ollama(prompt)
