"""
adblock.py
------------------------
Feature #10 (part 1) for Sounix: block known ad/malware domains by
editing /etc/hosts on THIS machine.

Redirects known-bad domains to 0.0.0.0 so they fail to resolve.
This only affects the machine Sounix is running on -- it does not
block anything on other devices or the network as a whole.
"""

import subprocess

HOSTS_FILE = "/etc/hosts"
START_MARKER = "# SOUNIX-ADBLOCK-START"
END_MARKER = "# SOUNIX-ADBLOCK-END"

# A small, curated starter list. Not exhaustive -- a real-world
# blocklist has thousands of entries, but this proves the mechanism
# works correctly before scaling up.
BLOCKED_DOMAINS = [
    "doubleclick.net",
    "googlesyndication.com",
    "googleadservices.com",
    "adnxs.com",
    "adsrvr.org",
    "popads.net",
    "malwaredomainlist.com",
    "trackad.click",
]


def _read_hosts():
    with open(HOSTS_FILE, "r") as f:
        return f.read()


def is_blocklist_enabled():
    return START_MARKER in _read_hosts()


def enable_blocklist():
    if is_blocklist_enabled():
        return "Sounix: Blocklist is already enabled."

    lines = [START_MARKER]
    for domain in BLOCKED_DOMAINS:
        lines.append(f"0.0.0.0 {domain}")
    lines.append(END_MARKER)

    block_text = "\n".join(lines) + "\n"

    try:
        # Write the block to a temp file, then use sudo tee to append
        # it to /etc/hosts, since Sounix itself doesn't run as root.
        result = subprocess.run(
            ["sudo", "tee", "-a", HOSTS_FILE],
            input=block_text,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return f"Sounix: Failed to enable blocklist: {result.stderr.strip()}"

        return f"Sounix: Blocklist enabled. {len(BLOCKED_DOMAINS)} domain(s) blocked."
    except Exception as e:
        return f"Sounix: Error enabling blocklist: {str(e)}"


def disable_blocklist():
    if not is_blocklist_enabled():
        return "Sounix: Blocklist is not currently enabled."

    content = _read_hosts()
    lines = content.split("\n")

    new_lines = []
    inside_block = False
    for line in lines:
        if line.strip() == START_MARKER:
            inside_block = True
            continue
        if line.strip() == END_MARKER:
            inside_block = False
            continue
        if not inside_block:
            new_lines.append(line)

    new_content = "\n".join(new_lines)

    try:
        result = subprocess.run(
            ["sudo", "tee", HOSTS_FILE],
            input=new_content,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return f"Sounix: Failed to disable blocklist: {result.stderr.strip()}"

        return "Sounix: Blocklist disabled. /etc/hosts restored."
    except Exception as e:
        return f"Sounix: Error disabling blocklist: {str(e)}"


def blocklist_status():
    if is_blocklist_enabled():
        return f"Sounix: Blocklist is ENABLED. {len(BLOCKED_DOMAINS)} domain(s) blocked."
    return "Sounix: Blocklist is DISABLED."
