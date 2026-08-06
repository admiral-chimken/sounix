import tkinter as tk
from tkinter import scrolledtext

from ai import respond
from settings import settings_report

from file_manager import (
    list_files,
    make_folder,
    copy_file,
    move_file,
    rename_file,
    delete_file,
)


def open_settings():
    window = tk.Toplevel(root)
    window.title("Sounix Settings")
    window.geometry("650x500")

    output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Monospace", 11),
    )

    output.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10,
    )

    output.insert(
        tk.END,
        settings_report()
    )

    output.configure(state="disabled")


def open_about():
    window = tk.Toplevel(root)
    window.title("About Sounix")
    window.geometry("500x400")

    text = """
◉ SOUNIX

Linux Personal Assistant

Version: 1.0.0

Built with:
- Python
- Linux
- Tkinter

Features:
✓ System information
✓ Firewall control
✓ VPN support
✓ Tailscale support
✓ File management
✓ Memory system
✓ Network tools

Status:
Active Development
"""

    label = tk.Label(
        window,
        text=text,
        font=("Sans", 12),
        justify="left",
    )

    label.pack(
        padx=20,
        pady=20,
    )


def open_files():
    window = tk.Toplevel(root)
    window.title("Sounix File Manager")
    window.geometry("700x500")

    path_entry = tk.Entry(window)
    path_entry.pack(
        fill="x",
        padx=10,
        pady=5,
    )

    path_entry.insert(0, "~")

    output = scrolledtext.ScrolledText(window)
    output.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5,
    )

    def show_files():
        output.delete("1.0", tk.END)
        output.insert(
            tk.END,
            list_files(path_entry.get())
        )

    button = tk.Button(
        window,
        text="List Files",
        command=show_files,
    )

    button.pack(
        pady=5
    )


def run_command():

    command = command_entry.get().strip()

    if not command:
        return

    output_box.insert(
        tk.END,
        f"You: {command}\n"
    )

    try:
        answer = respond(command)

        output_box.insert(
            tk.END,
            f"{answer}\n\n"
        )

    except Exception as error:

        output_box.insert(
            tk.END,
            f"Sounix Error: {error}\n\n"
        )

    output_box.see(tk.END)

    command_entry.delete(
        0,
        tk.END
    )


def use_command(command):

    if command == "settings":
        open_settings()
        return

    if command == "files":
        open_files()
        return

    if command == "about":
        open_about()
        return

    command_entry.delete(
        0,
        tk.END
    )

    command_entry.insert(
        0,
        command
    )

    run_command()



root = tk.Tk()

root.title("Sounix")
root.geometry("950x850")


logo_label = tk.Label(
    root,
    text="◉ SOUNIX",
    font=("Sans", 32, "bold"),
)

logo_label.pack(
    pady=(10,2)
)


subtitle_label = tk.Label(
    root,
    text="Linux System Assistant",
    font=("Sans", 12),
)

subtitle_label.pack(
    pady=(0,10)
)



button_frame = tk.Frame(root)

button_frame.pack(
    padx=15,
    pady=5,
    fill="x",
)



sections = {

    "System": [
        ("System Info", "system"),
        ("Doctor", "doctor"),
        ("Distro", "distro"),
        ("Settings", "settings"),
    ],


    "Security": [
        ("Firewall Status", "firewall status"),
        ("Enable Firewall", "enable firewall"),
        ("Disable Firewall", "disable firewall"),
        ("VPN Status", "vpn status"),
        ("Tailscale", "tailscale status"),
        ("Cyber Center", "security"),
        ("Network Scan", "network scan"),
    ],


    "Files": [
        ("Files", "files"),
    ],


    "Assistant": [
        ("Memory", "memories"),
        ("Travel Mode", "travel mode"),
        ("Help", "help"),
        ("About", "about"),
    ],

}



row = 0


for section, buttons in sections.items():

    title = tk.Label(
        button_frame,
        text=section,
        font=("Sans", 12, "bold"),
    )

    title.grid(
        row=row,
        column=0,
        columnspan=5,
        sticky="w",
        pady=5,
    )

    row += 1

    column = 0


    for label, command in buttons:

        button = tk.Button(
            button_frame,
            text=label,
            width=16,
            height=2,
            command=lambda value=command: use_command(value),
        )

        button.grid(
            row=row,
            column=column,
            padx=5,
            pady=5,
        )

        column += 1


        if column == 5:
            column = 0
            row += 1


    row += 1



output_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    font=("Monospace", 11),
)

output_box.pack(
    padx=15,
    pady=10,
    fill="both",
    expand=True,
)

output_box.configure(
    height=12
)



command_frame = tk.Frame(root)

command_frame.pack(
    padx=15,
    pady=10,
    fill="x",
)



command_entry = tk.Entry(
    command_frame,
    font=("Sans", 12),
)


command_entry.pack(
    side="left",
    fill="x",
    expand=True,
)



run_button = tk.Button(
    command_frame,
    text="Run",
    command=run_command,
    width=10,
)


run_button.pack(
    side="right"
)



command_entry.bind(
    "<Return>",
    lambda event: run_command()
)



output_box.insert(
    tk.END,
    "Sounix GUI ready.\n"
    "Enter a command or use a button.\n\n"
)


command_entry.focus()


root.mainloop()
