"""
migrate_memory.py
------------------------
One-time migration script: finds any plaintext (non-encrypted)
entries in sounix_memory.json and re-saves them through remember(),
which will encrypt them going forward.

Run this ONCE after upgrading to the encrypted memory.py.
"""

from memory import load_memory, remember, ENC_PREFIX


def migrate():
    raw_memory = load_memory()
    migrated = []

    for key, value in list(raw_memory.items()):
        already_encrypted = isinstance(value, str) and value.startswith(ENC_PREFIX)
        if not already_encrypted:
            remember(key, value)  # re-saves it, now encrypted
            migrated.append(key)

    if migrated:
        print(f"Migrated {len(migrated)} entr(y/ies): {', '.join(migrated)}")
    else:
        print("Nothing to migrate -- everything is already encrypted.")


if __name__ == "__main__":
    migrate()
