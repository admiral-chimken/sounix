"""
predictive_analytics.py
------------------------
Feature #2 for Sounix.
"""

from memory import list_memories
from ollama_client import ask_ollama

SAFE_KEYS = {
    "firewall",
    "last_update_check",
    "distro",
    "hostname",
}


def summarize_state(memory):
    if not memory:
        return "No data has been recorded yet."

    lines = []
    skipped = 0
    for key, value in memory.items():
        if key.lower() not in SAFE_KEYS:
            skipped += 1
            continue
        lines.append(f"- {key}: {value}")

    if not lines:
        return "No approved data is available to analyze."

    header = f"Sounix currently remembers {len(lines)} approved item(s):"
    if skipped:
        header += f" ({skipped} other item(s) excluded by default)"

    return "\n".join([header] + lines)


def run_predictive_analytics():
    memory = list_memories()
    summary = summarize_state(memory)

    prompt = (
        "Here is the current remembered security state of this machine:"
        f"\n\n{summary}\n\n"
        "Based on this snapshot, give a short (3-5 sentence) prediction "
        "of what security risks are most likely if nothing changes, "
        "and one concrete recommendation. Note that this is a "
        "single snapshot, not historical trend data, so don't claim "
        "to see trends over time."
    )

    return ask_ollama(prompt)


if __name__ == "__main__":
    print(run_predictive_analytics())
