"""
mfa_checklist.py
------------------------
Feature #3 (second half) for Sounix: a simple tracker for which of
your accounts have multi-factor authentication enabled.

This does NOT check anything automatically -- it's a manual
checklist you update yourself, since Sounix has no way to actually
verify MFA status on external services like GitHub or your email.
"""

from memory import recall, remember

MFA_KEY = "mfa_accounts"


def _load_accounts():
    accounts = recall(MFA_KEY)
    return accounts if accounts else {}


def track_account(name):
    name = name.strip().lower()
    if not name:
        return "Sounix: Use: track account <name>"

    accounts = _load_accounts()
    if name in accounts:
        return f"Sounix: {name} is already being tracked."

    accounts[name] = False
    remember(MFA_KEY, accounts)
    return f"Sounix: Now tracking {name}. Use 'mfa enabled {name}' once you've turned on MFA for it."


def mark_mfa_enabled(name):
    name = name.strip().lower()
    accounts = _load_accounts()

    if name not in accounts:
        return f"Sounix: {name} isn't being tracked yet. Use 'track account {name}' first."

    accounts[name] = True
    remember(MFA_KEY, accounts)
    return f"Sounix: Marked {name} as MFA-enabled."


def mfa_status():
    accounts = _load_accounts()

    if not accounts:
        return "Sounix: No accounts tracked yet. Use 'track account <name>' to start."

    lines = ["Sounix: MFA Checklist:"]
    for name, enabled in accounts.items():
        mark = "[x]" if enabled else "[ ]"
        lines.append(f"  {mark} {name}")

    missing = [n for n, e in accounts.items() if not e]
    if missing:
        lines.append(f"\n{len(missing)} account(s) still need MFA enabled.")
    else:
        lines.append("\nAll tracked accounts have MFA enabled.")

    return "\n".join(lines)
