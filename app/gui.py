import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from updater import check_updates
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

try:
    from version import SOUNIX_VERSION
except ImportError:
    SOUNIX_VERSION = "1.0.0"


# -----------------------------
# Theme
# -----------------------------

BACKGROUND = "#111827"
PANEL = "#1f2937"
PANEL_LIGHT = "#374151"
TEXT = "#f9fafb"
MUTED_TEXT = "#cbd5e1"
ACCENT = "#38bdf8"
DANGER = "#ef4444"
ENTRY_BACKGROUND = "#0f172a"


def configure_theme():
    style = ttk.Style()

    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "TFrame",
        background=BACKGROUND,
    )

    style.configure(
        "Panel.TFrame",
        background=PANEL,
    )

    style.configure(
        "TLabel",
        background=BACKGROUND,
        foreground=TEXT,
        font=("Sans", 11),
    )

    style.configure(
        "Header.TLabel",
        background=BACKGROUND,
        foreground=ACCENT,
        font=("Sans", 28, "bold"),
    )

    style.configure(
        "Subtitle.TLabel",
        background=BACKGROUND,
        foreground=MUTED_TEXT,
        font=("Sans", 11),
    )

    style.configure(
        "Status.TLabel",
        background=BACKGROUND,
        foreground=MUTED_TEXT,
        font=("Sans", 10),
    )

    style.configure(
        "TButton",
        font=("Sans", 10),
        padding=(10, 8),
        background=PANEL_LIGHT,
        foreground=TEXT,
    )

    style.map(
        "TButton",
        background=[
            ("active", ACCENT),
            ("pressed", ACCENT),
        ],
        foreground=[
            ("active", BACKGROUND),
            ("pressed", BACKGROUND),
        ],
    )

    style.configure(
        "Danger.TButton",
        font=("Sans", 10),
        padding=(10, 8),
        background=DANGER,
        foreground=TEXT,
    )

    style.map(
        "Danger.TButton",
        background=[
            ("active", "#dc2626"),
            ("pressed", "#b91c1c"),
        ],
    )

    style.configure(
        "TNotebook",
        background=BACKGROUND,
        borderwidth=0,
    )

    style.configure(
        "TNotebook.Tab",
        background=PANEL,
        foreground=TEXT,
        padding=(14, 8),
        font=("Sans", 10, "bold"),
    )

    style.map(
        "TNotebook.Tab",
        background=[("selected", ACCENT)],
        foreground=[("selected", BACKGROUND)],
    )


# -----------------------------
# Output helpers
# -----------------------------

def write_output(text):
    output_box.configure(state="normal")
    output_box.insert(tk.END, str(text))
    output_box.see(tk.END)
    output_box.configure(state="disabled")


def clear_output():
    output_box.configure(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.configure(state="disabled")


def set_busy(is_busy):
    if is_busy:
        status_var.set("Working...")
        run_button.configure(state="disabled")
    else:
        status_var.set("Ready")
        run_button.configure(state="normal")
        command_entry.focus_set()


# -----------------------------
# Command handling
# -----------------------------

def finish_command(answer):
    write_output(f"Sounix: {answer}\n\n")
    set_busy(False)


def command_failed(error):
    write_output(f"Sounix GUI error: {error}\n\n")
    set_busy(False)


def process_command(command):
    try:
        answer = respond(command)
        root.after(0, finish_command, answer)
    except Exception as error:
        root.after(0, command_failed, error)


def run_command():
    command = command_entry.get().strip()

    if not command:
        status_var.set("Enter a command first.")
        command_entry.focus_set()
        return

    command_entry.delete(0, tk.END)
    write_output(f"You: {command}\n")
    set_busy(True)

    worker = threading.Thread(
        target=process_command,
        args=(command,),
        daemon=True,
    )
    worker.start()


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
    if command in {"about", "who are you", "creator"}:
        return (
            "Hello, I'm Sounix.\n\n"
            "I'm a cybersecurity-focused, multipurpose assistant created to help "
            "protect, manage, and better understand your computer.\n\n"
            "I may not be like ChatGPT, Claude, or other AI assistants, "
            "but I have my own purpose.\n\n"
            "I was built using Python, with Arch Linux as my original "
            "development environment.\n\n"
            "I'm still under active development, so new features will continue "
            "to be added over time.\n\n"
            "Created by AdmiralChimken.\n\n"
            "GitHub:\n"
            "https://github.com/admiral-chimken/sounix"
        )
    command_entry.delete(0, tk.END)
    command_entry.insert(0, command)
    run_command()


# -----------------------------
# Settings window
# -----------------------------

def open_settings():
    window = tk.Toplevel(root)
    window.title("Sounix Settings")
    window.geometry("700x520")
    window.configure(background=BACKGROUND)

    title = ttk.Label(
        window,
        text="Sounix Settings",
        style="Header.TLabel",
    )
    title.pack(pady=(16, 8))

    output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Monospace", 11),
        background=ENTRY_BACKGROUND,
        foreground=TEXT,
        insertbackground=TEXT,
        relief="flat",
        padx=12,
        pady=12,
    )
    output.pack(
        fill="both",
        expand=True,
        padx=16,
        pady=(0, 16),
    )

    try:
        report = settings_report()
    except Exception as error:
        report = f"Sounix could not load settings: {error}"

    output.insert(tk.END, report)
    output.configure(state="disabled")


# -----------------------------
# About window
# -----------------------------

def open_about():
    window = tk.Toplevel(root)
    window.title("About Sounix")
    window.geometry("520x430")
    window.configure(background=BACKGROUND)
    window.resizable(False, False)

    ttk.Label(
        window,
        text="◉ SOUNIX",
        style="Header.TLabel",
    ).pack(pady=(24, 4))

    ttk.Label(
        window,
        text="Linux System Assistant",
        style="Subtitle.TLabel",
    ).pack(pady=(0, 18))

    about_text = (
        f"Version: {SOUNIX_VERSION}\n\n"
        "Sounix is a Linux assistant built with Python and Tkinter.\n\n"
        "Current features include:\n"
        "• System information and diagnostics\n"
        "• Firewall controls with safety confirmations\n"
        "• VPN and Tailscale status\n"
        "• File management\n"
        "• Memory and calculator tools\n"
        "• Network and security tools\n"
        "• Software installation support\n"
        "• Update checking\n\n"
        "Status: Active development"
    )

    label = tk.Label(
        window,
        text=about_text,
        background=BACKGROUND,
        foreground=TEXT,
        justify="left",
        anchor="nw",
        font=("Sans", 11),
    )
    label.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=(0, 20),
    )


# -----------------------------
# File Manager window
# -----------------------------

def open_files():
    window = tk.Toplevel(root)
    window.title("Sounix File Manager")
    window.geometry("780x620")
    window.configure(background=BACKGROUND)

    ttk.Label(
        window,
        text="File Manager",
        style="Header.TLabel",
    ).pack(pady=(14, 6))

    form = ttk.Frame(window, style="Panel.TFrame")
    form.pack(
        fill="x",
        padx=16,
        pady=8,
    )

    ttk.Label(
        form,
        text="Source or path:",
        background=PANEL,
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=(10, 4),
    )

    path_entry = tk.Entry(
        form,
        font=("Sans", 11),
        background=ENTRY_BACKGROUND,
        foreground=TEXT,
        insertbackground=TEXT,
        relief="flat",
    )
    path_entry.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=10,
        pady=(0, 10),
    )
    path_entry.insert(0, "~")

    ttk.Label(
        form,
        text="Destination or new name:",
        background=PANEL,
    ).grid(
        row=0,
        column=1,
        sticky="w",
        padx=10,
        pady=(10, 4),
    )

    destination_entry = tk.Entry(
        form,
        font=("Sans", 11),
        background=ENTRY_BACKGROUND,
        foreground=TEXT,
        insertbackground=TEXT,
        relief="flat",
    )
    destination_entry.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=10,
        pady=(0, 10),
    )

    form.grid_columnconfigure(0, weight=1)
    form.grid_columnconfigure(1, weight=1)

    file_output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Monospace", 10),
        background=ENTRY_BACKGROUND,
        foreground=TEXT,
        insertbackground=TEXT,
        relief="flat",
        padx=10,
        pady=10,
    )
    file_output.pack(
        fill="both",
        expand=True,
        padx=16,
        pady=8,
    )

    def show_result(result):
        file_output.delete("1.0", tk.END)
        file_output.insert(tk.END, str(result))
        file_output.see(tk.END)

    def source():
        return path_entry.get().strip()

    def destination():
        return destination_entry.get().strip()

    def list_action():
        show_result(list_files(source()))

    def folder_action():
        show_result(make_folder(source()))

    def copy_action():
        if not source() or not destination():
            show_result("Sounix: Enter both a source and destination.")
            return
        show_result(copy_file(source(), destination()))

    def move_action():
        if not source() or not destination():
            show_result("Sounix: Enter both a source and destination.")
            return
        show_result(move_file(source(), destination()))

    def rename_action():
        if not source() or not destination():
            show_result("Sounix: Enter a source and new name.")
            return
        show_result(rename_file(source(), destination()))

    def delete_action():
        if not source():
            show_result("Sounix: Enter a file or folder path.")
            return
        show_result(delete_file(source()))

    controls = ttk.Frame(window)
    controls.pack(
        fill="x",
        padx=16,
        pady=(4, 16),
    )

    actions = [
        ("List Files", list_action, "TButton"),
        ("Make Folder", folder_action, "TButton"),
        ("Copy", copy_action, "TButton"),
        ("Move", move_action, "TButton"),
        ("Rename", rename_action, "TButton"),
        ("Delete", delete_action, "Danger.TButton"),
    ]

    for index, (label, callback, style_name) in enumerate(actions):
        button = ttk.Button(
            controls,
            text=label,
            command=callback,
            style=style_name,
        )
        button.grid(
            row=index // 3,
            column=index % 3,
            sticky="ew",
            padx=5,
            pady=5,
        )

    for column in range(3):
        controls.grid_columnconfigure(column, weight=1)
def check_updates_on_startup():
    status_var.set("Checking for updates...")

    def worker():
        try:
            result = check_updates()
            root.after(0, show_startup_update_result, result)
        except Exception as error:
            root.after(
                0,
                show_startup_update_result,
                f"Sounix update check failed: {error}",
            )

    threading.Thread(
        target=worker,
        daemon=True,
    ).start()


def show_startup_update_result(result):
    write_output(f"{result}\n\n")
    status_var.set("Ready")

# -----------------------------
# Main window
# -----------------------------

root = tk.Tk()
root.title(f"Sounix {SOUNIX_VERSION}")
root.geometry("980x760")
root.minsize(760, 620)
root.configure(background=BACKGROUND)

configure_theme()

root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

header = ttk.Frame(root)
header.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=18,
    pady=(14, 6),
)
header.grid_columnconfigure(0, weight=1)

ttk.Label(
    header,
    text="◉ SOUNIX",
    style="Header.TLabel",
).grid(
    row=0,
    column=0,
    sticky="w",
)

ttk.Label(
    header,
    text="Linux System Assistant",
    style="Subtitle.TLabel",
).grid(
    row=1,
    column=0,
    sticky="w",
)

status_var = tk.StringVar(value="Ready")

ttk.Label(
    header,
    textvariable=status_var,
    style="Status.TLabel",
).grid(
    row=0,
    column=1,
    rowspan=2,
    sticky="e",
)

notebook = ttk.Notebook(root)
notebook.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=18,
    pady=6,
)

sections = {
    "System": [
        ("System Info", "system", "TButton"),
        ("Doctor", "doctor", "TButton"),
        ("Distro", "distro", "TButton"),
        ("Settings", "settings", "TButton"),
        ("Check Updates", "check updates", "TButton"),
    ],
    "Security": [
        ("Firewall Status", "firewall status", "TButton"),
        ("Enable Firewall", "enable firewall", "TButton"),
        ("Disable Firewall", "disable firewall", "Danger.TButton"),
        ("VPN Status", "vpn status", "TButton"),
        ("Tailscale", "tailscale status", "TButton"),
        ("Cyber Center", "security", "TButton"),
        ("Network Scan", "network scan", "TButton"),
    ],
    "Files": [
        ("File Manager", "files", "TButton"),
        ("List Home", "list ~", "TButton"),
    ],
    "Assistant": [
        ("Memory", "memories", "TButton"),
        ("Travel Mode", "travel mode", "TButton"),
        ("Help", "help", "TButton"),
        ("About", "about", "TButton"),
    ],
}

for section_name, buttons in sections.items():
    tab = ttk.Frame(notebook, style="Panel.TFrame")
    notebook.add(tab, text=section_name)

    for index, (label, command, style_name) in enumerate(buttons):
        button = ttk.Button(
            tab,
            text=label,
            command=lambda value=command: use_command(value),
            style=style_name,
        )
        button.grid(
            row=index // 4,
            column=index % 4,
            sticky="ew",
            padx=7,
            pady=8,
        )

    for column in range(4):
        tab.grid_columnconfigure(column, weight=1)

output_frame = ttk.Frame(root, style="Panel.TFrame")
output_frame.grid(
    row=2,
    column=0,
    sticky="nsew",
    padx=18,
    pady=8,
)
output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

output_box = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    font=("Monospace", 11),
    background=ENTRY_BACKGROUND,
    foreground=TEXT,
    insertbackground=TEXT,
    relief="flat",
    padx=12,
    pady=12,
)
output_box.grid(
    row=0,
    column=0,
    sticky="nsew",
    padx=8,
    pady=8,
)
output_box.configure(state="disabled")

command_frame = ttk.Frame(root)
command_frame.grid(
    row=3,
    column=0,
    sticky="ew",
    padx=18,
    pady=(6, 16),
)
command_frame.grid_columnconfigure(0, weight=1)

command_entry = tk.Entry(
    command_frame,
    font=("Sans", 12),
    background=ENTRY_BACKGROUND,
    foreground=TEXT,
    insertbackground=TEXT,
    relief="flat",
)
command_entry.grid(
    row=0,
    column=0,
    sticky="ew",
    ipady=9,
    padx=(0, 8),
)

run_button = ttk.Button(
    command_frame,
    text="Run",
    command=run_command,
)
run_button.grid(
    row=0,
    column=1,
    padx=(0, 8),
)

clear_button = ttk.Button(
    command_frame,
    text="Clear",
    command=clear_output,
)
clear_button.grid(
    row=0,
    column=2,
)

command_entry.bind(
    "<Return>",
    lambda event: run_command(),
)

write_output(
    f"Sounix {SOUNIX_VERSION} ready.\n"
    "Enter a command below or choose a dashboard action.\n\n"
)

command_entry.focus_set()

root.after(1000, check_updates_on_startup)

root.mainloop()
