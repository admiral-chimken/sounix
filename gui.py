import tkinter as tk
from tkinter import scrolledtext

from ai import respond
from file_manager import (
    list_files,
    make_folder,
    copy_file,
    move_file,
    rename_file,
    delete_file,
)
from settings import settings_report


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

    output.insert(tk.END, settings_report())
    output.configure(state="disabled")


def open_about():
    window = tk.Toplevel(root)
    window.title("About Sounix")
    window.geometry("520x460")

    about_text = (
        "SOUNIX\n\n"
        "Linux Personal Assistant\n\n"
        "Version: 1.0 Beta\n\n"
        "Created by William\n\n"
        "Built with:\n"
        "- Python\n"
        "- Linux\n"
        "- Tkinter\n\n"
        "Features:\n"
        "- System information\n"
        "- File management\n"
        "- Security tools\n"
        "- Firewall controls\n"
        "- VPN and Tailscale status\n"
        "- Network scanning\n"
        "- Package management\n"
        "- Memory system\n"
        "- Settings dashboard\n\n"
        "Status: Active Development"
    )

    label = tk.Label(
        window,
        text=about_text,
        justify="left",
        anchor="nw",
        font=("Sans", 12),
    )
    label.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=20,
    )


def open_files():
    window = tk.Toplevel(root)
    window.title("Sounix File Manager")
    window.geometry("760x600")

    path_label = tk.Label(
        window,
        text="Folder or file path:",
        font=("Sans", 11, "bold"),
    )
    path_label.pack(
        anchor="w",
        padx=10,
        pady=(10, 2),
    )

    path_entry = tk.Entry(
        window,
        font=("Sans", 11),
    )
    path_entry.pack(
        fill="x",
        padx=10,
        pady=5,
    )
    path_entry.insert(0, "~")

    second_label = tk.Label(
        window,
        text="Destination or new name:",
        font=("Sans", 11, "bold"),
    )
    second_label.pack(
        anchor="w",
        padx=10,
        pady=(5, 2),
    )

    second_entry = tk.Entry(
        window,
        font=("Sans", 11),
    )
    second_entry.pack(
        fill="x",
        padx=10,
        pady=5,
    )

    output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Monospace", 10),
    )
    output.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10,
    )

    def show_result(result):
        output.delete("1.0", tk.END)
        output.insert(tk.END, str(result))

    def show_files():
        show_result(list_files(path_entry.get().strip()))

    def create_folder():
        show_result(make_folder(path_entry.get().strip()))

    def copy_selected():
        source = path_entry.get().strip()
        destination = second_entry.get().strip()

        if not source or not destination:
            show_result("Sounix: Enter a source and destination.")
            return

        show_result(copy_file(source, destination))

    def move_selected():
        source = path_entry.get().strip()
        destination = second_entry.get().strip()

        if not source or not destination:
            show_result("Sounix: Enter a source and destination.")
            return

        show_result(move_file(source, destination))

    def rename_selected():
        source = path_entry.get().strip()
        new_name = second_entry.get().strip()

        if not source or not new_name:
            show_result("Sounix: Enter a source and new name.")
            return

        show_result(rename_file(source, new_name))

    def delete_selected():
        path = path_entry.get().strip()

        if not path:
            show_result("Sounix: Enter a file or folder path.")
            return

        show_result(delete_file(path))

    button_frame = tk.Frame(window)
    button_frame.pack(
        padx=10,
        pady=(0, 10),
        fill="x",
    )

    file_buttons = [
        ("List Files", show_files),
        ("Make Folder", create_folder),
        ("Copy", copy_selected),
        ("Move", move_selected),
        ("Rename", rename_selected),
        ("Delete", delete_selected),
    ]

    for index, (label, action) in enumerate(file_buttons):
        button = tk.Button(
            button_frame,
            text=label,
            command=action,
            width=14,
        )
        button.grid(
            row=index // 3,
            column=index % 3,
            padx=5,
            pady=5,
            sticky="ew",
        )

    for column in range(3):
        button_frame.grid_columnconfigure(column, weight=1)


def run_command():
    command = command_entry.get().strip()

    if not command:
        return

    output_box.insert(tk.END, f"You: {command}\n")

    try:
        answer = respond(command)
        output_box.insert(tk.END, f"{answer}\n\n")

    except Exception as error:
        output_box.insert(
            tk.END,
            f"Sounix GUI error: {error}\n\n",
        )

    output_box.see(tk.END)
    command_entry.delete(0, tk.END)
       


def use_command(command):
    if command == "files":
        open_files()
        return

    if command == "settings":
        open_settings()
        return

    if command == "about":
        open_about()
        return

    command_entry.delete(0, tk.END)
    command_entry.insert(0, command)
    run_command()


root = tk.Tk()
root.title("Sounix")
root.geometry("950x900")
root.minsize(760, 600)

title_label = tk.Label(
    root,
    text="SOUNIX",
    font=("Sans", 25, "bold"),
)
title_label.pack(pady=(15, 2))

subtitle_label = tk.Label(
    root,
    text="Linux System Assistant",
    font=("Sans", 11),
)
subtitle_label.pack(pady=(0, 12))

button_frame = tk.Frame(root)
button_frame.pack(
    padx=15,
    pady=5,
    fill="x",
)
button_frame.pack_propagate(False)
button_frame.configure(height=260)

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
        ("File Manager", "files"),
    ],

    "Assistant": [
        ("Memory", "memories"),
        ("Travel Mode", "travel mode"),
        ("Help", "help"),
        ("About", "about"),
    ],
}

row = 0

for section_name, section_buttons in sections.items():
    section_label = tk.Label(
        button_frame,
        text=section_name,
        font=("Sans", 12, "bold"),
        anchor="w",
    )
    section_label.grid(
        row=row,
        column=0,
        columnspan=5,
        padx=5,
        pady=(8, 3),
        sticky="w",
    )

    row += 1
    column = 0

    for label, command in section_buttons:
        button = tk.Button(
            button_frame,
            text=label,
            command=lambda value=command: use_command(value),
            width=16,
            height=2,
        )
        button.grid(
            row=row,
            column=column,
            padx=5,
            pady=5,
            sticky="ew",
        )

        column += 1

        if column == 5:
            column = 0
            row += 1

    row += 1

for column in range(5):
    button_frame.grid_columnconfigure(column, weight=1)

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
output_box.pack(
    padx=15,
    pady=10,
    fill="both",
    expand=True,
)
output_box.configure(height=12)

command_frame = tk.Frame(root)
command_frame.pack(
    padx=15,
    pady=(0, 15),
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
    padx=(0, 8),
)

run_button = tk.Button(
    command_frame,
    text="Run",
    command=run_command,
    width=10,
)
run_button.pack(side="right")

command_entry.bind(
    "<Return>",
    lambda event: run_command(),
)

output_box.insert(
    tk.END,
    "Sounix GUI ready.\n"
    "Enter a command below or use one of the buttons.\n\n",
)

command_entry.focus()

root.mainloop()
