"""
auth.py
------------------------
Feature #3 for Sounix: PIN gate before the app opens.

Uses a hash of the PIN (not the raw PIN) for slightly better safety
if sounix_memory.json is ever exposed -- same idea as a real login
system never storing your actual password.
"""

import hashlib
import tkinter as tk
from tkinter import simpledialog

from memory import recall, remember


def _hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def check_pin():
    """
    Call this BEFORE creating the main window. Blocks until a correct
    PIN is entered (or first-time setup is completed), or exits the
    program entirely if cancelled or too many wrong attempts.
    """
    temp_root = tk.Tk()
    temp_root.withdraw()  # hide the temporary window, we only need it for dialogs

    stored_hash = recall("pin_hash")

    if stored_hash is None:
        # First time ever running Sounix -- set up a new PIN.
        while True:
            pin = simpledialog.askstring(
                "Set Up Sounix PIN",
                "No PIN is set yet. Create a PIN (4+ digits):",
                show="*",
                parent=temp_root,
            )
            if pin is None:
                temp_root.destroy()
                raise SystemExit("Sounix: PIN setup cancelled.")
            if len(pin) < 4:
                continue

            confirm = simpledialog.askstring(
                "Confirm PIN",
                "Enter the same PIN again to confirm:",
                show="*",
                parent=temp_root,
            )
            if pin == confirm:
                remember("pin_hash", _hash_pin(pin))
                break

        temp_root.destroy()
        return True

    # Normal login -- verify against the stored hash.
    for attempt in range(3):
        pin = simpledialog.askstring(
            "Sounix Login",
            "Enter your PIN:",
            show="*",
            parent=temp_root,
        )
        if pin is None:
            temp_root.destroy()
            raise SystemExit("Sounix: Login cancelled.")
        if _hash_pin(pin) == stored_hash:
            temp_root.destroy()
            return True

    temp_root.destroy()
    raise SystemExit("Sounix: Too many incorrect PIN attempts.")
