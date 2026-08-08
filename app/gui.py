import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

from ai import respond
from file_manager import (
    copy_file,
    delete_file,
    list_files,
    make_folder,
    move_file,
    rename_file,
)
from settings import settings_report
from updater import check_updates

try:
    from version import SOUNIX_VERSION
except ImportError:
    SOUNIX_VERSION = "1.0.0-beta"


# =========================================================
# COLORS
# =========================================================

BACKGROUND = "#111827"
PANEL = "#1f2937"
PANEL_LIGHT = "#374151"
ENTRY_BACKGROUND = "#0f172a"

TEXT = "#f9fafb"
MUTED_TEXT = "#cbd5e1"
ACCENT = "#38bdf8"
DANGER = "#ef4444"


# =========================================================
# THEME
# =========================================================

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
        font=("Sans", 10),
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
        font=("Sans", 10),
    )

    style.configure(
        "Status.TLabel",
        background=BACKGROUND,
        foreground=MUTED_TEXT,
        font=("Sans", 10, "bold"),
    )

    style.configure(
        "Section.TLabel",
        background=PANEL,
        foreground=ACCENT,
        font=("Sans", 11, "bold"),
    )

    style.configure(
        "TButton",
        background=PANEL_LIGHT,
        foreground=TEXT,
        font=("Sans", 9),
        padding=(6, 3),
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
        background=DANGER,
        foreground=TEXT,
        font=("Sans", 9),
        padding=(6, 3),
    )

    style.map(
        "Danger.TButton",
        background=[
            ("active", "#dc2626"),
            ("pressed", "#b91c1c"),
        ],
    )


# =========================================================
# OUTPUT
# =========================================================

def write_output(text):
    output_box.configure(state="normal")
    output_box.insert(tk.END, str(text))
    output_box.see(tk.END)
    output_box.configure(state="disabled")


def clear_output():
    output_box.configure(state="normal")
    output_box.delete("1.0", tk.END)
    output_box.configure(state="disabled")

    status_var.set("Ready")
    system_status_var.set("Ready")
    security_status_var.set("Not checked")


def set_busy(is_busy):
    if is_busy:
        status_var.set("Working...")
        run_button.configure(state="disabled")
    else:
        status_var.set("Ready")
        run_button.configure(state="normal")
        command_entry.focus_set()


# =========================================================
# COMMAND HANDLING
# =========================================================

def update_dashboard_status(command, answer):
    command = command.lower()
    answer_text = str(answer).lower()

    if command in {
        "system",
        "system info",
        "status",
        "doctor",
        "distro",
    }:
        system_status_var.set("Checked")

    if command in {
        "security",
        "health",
        "system health",
        "security health",
        "health report",
        "firewall",
        "firewall status",
        "vpn",
        "vpn status",
        "tailscale",
        "tailscale status",
        "network scan",
    }:
        security_status_var.set("Checked")

    if command == "check updates":
        if "up to date" in answer_text:
            updates_status_var.set("Up to date")
        elif "update is available" in answer_text:
            updates_status_var.set("Update available")
        elif "could not" in answer_text or "error" in answer_text:
            updates_status_var.set("Check failed")
        else:
            updates_status_var.set("Checked")

    if command == "update sounix":
        if "successfully" in answer_text:
            updates_status_var.set("Updated")
        elif "already up to date" in answer_text:
            updates_status_var.set("Up to date")
        else:
            updates_status_var.set("Update incomplete")


def finish_command(command, answer):
    write_output(f"{answer}\n\n")
    update_dashboard_status(command, answer)
    set_busy(False)


def command_failed(error):
    write_output(f"Sounix GUI error: {error}\n\n")
    set_busy(False)


def process_command(command):
    try:
        answer = respond(command)

        root.after(
            0,
            finish_command,
            command,
            answer,
        )

    except Exception as error:
        root.after(
            0,
            command_failed,
            error,
        )


def run_command():
    command = command_entry.get().strip()

    if not command:
        status_var.set("Enter a command first.")
        command_entry.focus_set()
        return

    command_entry.delete(0, tk.END)

    write_output(
        f"You: {command}\n"
    )

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

    command_entry.delete(0, tk.END)
    command_entry.insert(0, command)

    run_command()


# =========================================================
# STARTUP UPDATE CHECK
# =========================================================

def show_startup_update_result(result):
    result_text = str(result)

    write_output(
        f"{result_text}\n\n"
    )

    lower_result = result_text.lower()

    if "up to date" in lower_result:
        updates_status_var.set("Up to date")

    elif "update is available" in lower_result:
        updates_status_var.set("Update available")

    elif "could not" in lower_result or "error" in lower_result:
        updates_status_var.set("Check failed")

    else:
        updates_status_var.set("Checked")

    status_var.set("Ready")


def check_updates_on_startup():
    status_var.set("Checking for updates...")
    updates_status_var.set("Checking...")

    def worker():
        try:
            result = check_updates()

        except Exception as error:
            result = (
                f"Sounix update check failed: {error}"
            )

        root.after(
            0,
            show_startup_update_result,
            result,
        )

    threading.Thread(
        target=worker,
        daemon=True,
    ).start()


# =========================================================
# SETTINGS WINDOW
# =========================================================

def open_settings():
    window = tk.Toplevel(root)

    window.title("Sounix Settings")
    window.geometry("700x520")
    window.configure(background=BACKGROUND)

    ttk.Label(
        window,
        text="Sounix Settings",
        style="Header.TLabel",
    ).pack(
        pady=(16, 8),
    )

    output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Sans", 11),
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
        report = (
            f"Sounix could not load settings: {error}"
        )

    output.insert(
        tk.END,
        report,
    )

    output.configure(
        state="disabled",
    )


# =========================================================
# ABOUT WINDOW
# =========================================================

def open_about():
    window = tk.Toplevel(root)

    window.title("About Sounix")
    window.geometry("600x550")
    window.configure(background=BACKGROUND)

    ttk.Label(
        window,
        text="◉ SOUNIX",
        style="Header.TLabel",
    ).pack(
        pady=(22, 4),
    )

    ttk.Label(
        window,
        text="Cybersecurity & Multipurpose Linux Assistant",
        style="Subtitle.TLabel",
    ).pack(
        pady=(0, 18),
    )

    about_text = (
        f"Version: {SOUNIX_VERSION}\n\n"
        "Hello. I'm Sounix.\n\n"
        "I'm a cybersecurity-focused, multipurpose assistant created "
        "to help users protect, manage, and better understand their "
        "computer systems.\n\n"
        "I may not be like ChatGPT, Claude, or other large AI systems, "
        "but I am an assistant with my own purpose.\n\n"
        "I was built using Python, with Arch Linux as my original "
        "development environment.\n\n"
        "Sounix is still under active development. New features, "
        "improvements, and fixes may take time.\n\n"
        "Created and developed by AdmiralChimken.\n\n"
        "Feedback, bug reports, and suggestions:\n"
        "https://github.com/admiral-chimken/sounix"
    )

    about_label = tk.Label(
        window,
        text=about_text,
        background=BACKGROUND,
        foreground=TEXT,
        justify="left",
        anchor="nw",
        wraplength=530,
        font=("Sans", 11),
    )

    about_label.pack(
        fill="both",
        expand=True,
        padx=30,
        pady=(0, 20),
    )


# =========================================================
# FILE MANAGER WINDOW
# =========================================================

def open_files():
    window = tk.Toplevel(root)

    window.title("Sounix File Manager")
    window.geometry("780x620")
    window.configure(background=BACKGROUND)

    ttk.Label(
        window,
        text="File Manager",
        style="Header.TLabel",
    ).pack(
        pady=(14, 6),
    )

    form = ttk.Frame(
        window,
        style="Panel.TFrame",
    )

    form.pack(
        fill="x",
        padx=16,
        pady=8,
    )

    tk.Label(
        form,
        text="Source or path:",
        background=PANEL,
        foreground=TEXT,
        font=("Sans", 10),
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

    path_entry.insert(
        0,
        "~",
    )

    tk.Label(
        form,
        text="Destination or new name:",
        background=PANEL,
        foreground=TEXT,
        font=("Sans", 10),
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

    form.grid_columnconfigure(
        0,
        weight=1,
    )

    form.grid_columnconfigure(
        1,
        weight=1,
    )

    file_output = scrolledtext.ScrolledText(
        window,
        wrap=tk.WORD,
        font=("Sans", 10),
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
        file_output.delete(
            "1.0",
            tk.END,
        )

        file_output.insert(
            tk.END,
            str(result),
        )

        file_output.see(
            tk.END,
        )

    def source():
        return path_entry.get().strip()

    def destination():
        return destination_entry.get().strip()

    def list_action():
        show_result(
            list_files(source())
        )

    def folder_action():
        show_result(
            make_folder(source())
        )

    def copy_action():
        if not source() or not destination():
            show_result(
                "Sounix: Enter both a source and destination."
            )
            return

        show_result(
            copy_file(
                source(),
                destination(),
            )
        )

    def move_action():
        if not source() or not destination():
            show_result(
                "Sounix: Enter both a source and destination."
            )
            return

        show_result(
            move_file(
                source(),
                destination(),
            )
        )

    def rename_action():
        if not source() or not destination():
            show_result(
                "Sounix: Enter a source and new name."
            )
            return

        show_result(
            rename_file(
                source(),
                destination(),
            )
        )

    def delete_action():
        if not source():
            show_result(
                "Sounix: Enter a file or folder path."
            )
            return

        show_result(
            delete_file(source())
        )

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
        controls.grid_columnconfigure(
            column,
            weight=1,
        )


# =========================================================
# DASHBOARD SECTION CREATOR
# =========================================================

def create_section(parent, title, buttons):
    section = ttk.Frame(
        parent,
        style="Panel.TFrame",
    )

    section.pack(
        fill="x",
        pady=1,
    )

    ttk.Label(
        section,
        text=title,
        style="Section.TLabel",
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=10,
        pady=(3, 2),
    )

    available_width = root.winfo_width()

    if available_width < 850:
        columns = 2
    elif available_width < 1150:
        columns = 3
    else:
        columns = 4

    for index, item in enumerate(buttons):
        label = item[0]
        command = item[1]

        if len(item) >= 3:
            style_name = item[2]
        else:
            style_name = "TButton"

        button = ttk.Button(
            section,
            text=label,
            command=lambda value=command: use_command(value),
            style=style_name,
        )

        button.grid(
            row=(index // columns) + 1,
            column=index % columns,
            sticky="ew",
            padx=4,
            pady=2,
        )

    for column in range(columns):
        section.grid_columnconfigure(
            column,
            weight=1,
        )


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title(
    f"Sounix {SOUNIX_VERSION}"
)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.90)
window_height = int(screen_height * 0.90)

window_width = max(
    800,
    min(window_width, 1400),
)

window_height = max(
    600,
    min(window_height, 1000),
)

root.geometry(
    f"{window_width}x{window_height}"
)

root.minsize(
    800,
    600,
)

root.configure(
    background=BACKGROUND,
)

configure_theme()

root.grid_columnconfigure(
    0,
    weight=1,
)

# Response area gets the flexible space.
root.grid_rowconfigure(
    2,
    weight=1,
    minsize=160,
)


# =========================================================
# HEADER
# =========================================================

header = tk.Frame(
    root,
    background=BACKGROUND,
)

header.grid(
    row=0,
    column=0,
    sticky="ew",
    padx=18,
    pady=(10, 5),
)

header.grid_columnconfigure(
    0,
    weight=1,
)

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
    text="Linux Cybersecurity & System Assistant",
    style="Subtitle.TLabel",
).grid(
    row=1,
    column=0,
    sticky="w",
)

status_var = tk.StringVar(
    value="Ready"
)

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


# =========================================================
# MAIN DASHBOARD
# =========================================================

dashboard_height = int(
    screen_height * 0.35
)

dashboard_height = max(
    210,
    min(dashboard_height, 330),
)

dashboard_holder = tk.Frame(
    root,
    background=BACKGROUND,
)

dashboard_holder.grid(
    row=1,
    column=0,
    sticky="ew",
    padx=18,
    pady=(2, 5),
)

dashboard_holder.grid_columnconfigure(
    0,
    weight=1,
)

dashboard_canvas = tk.Canvas(
    dashboard_holder,
    background=BACKGROUND,
    highlightthickness=0,
    height=dashboard_height,
)

dashboard_scrollbar = ttk.Scrollbar(
    dashboard_holder,
    orient="vertical",
    command=dashboard_canvas.yview,
)

dashboard_canvas.configure(
    yscrollcommand=dashboard_scrollbar.set,
)

dashboard_canvas.grid(
    row=0,
    column=0,
    sticky="ew",
)

dashboard_scrollbar.grid(
    row=0,
    column=1,
    sticky="ns",
)

dashboard_container = tk.Frame(
    dashboard_canvas,
    background=BACKGROUND,
)

dashboard_window = dashboard_canvas.create_window(
    (0, 0),
    window=dashboard_container,
    anchor="nw",
)


def update_dashboard_scrollregion(event=None):
    dashboard_canvas.configure(
        scrollregion=dashboard_canvas.bbox("all")
    )


def resize_dashboard_content(event):
    dashboard_canvas.itemconfigure(
        dashboard_window,
        width=event.width,
    )


def dashboard_mousewheel(event):
    if event.delta:
        direction = -1 if event.delta > 0 else 1

        dashboard_canvas.yview_scroll(
            direction,
            "units",
        )


dashboard_container.bind(
    "<Configure>",
    update_dashboard_scrollregion,
)

dashboard_canvas.bind(
    "<Configure>",
    resize_dashboard_content,
)

dashboard_canvas.bind(
    "<MouseWheel>",
    dashboard_mousewheel,
)


# =========================================================
# DASHBOARD STATUS
# =========================================================

system_status_var = tk.StringVar(
    value="Ready"
)

security_status_var = tk.StringVar(
    value="Not checked"
)

updates_status_var = tk.StringVar(
    value="Checking..."
)

status_panel = ttk.Frame(
    dashboard_container,
    style="Panel.TFrame",
)

status_panel.pack(
    fill="x",
    pady=(0, 4),
)

status_items = [
    ("System", system_status_var),
    ("Security", security_status_var),
    ("Updates", updates_status_var),
]

for index, (label_text, variable) in enumerate(status_items):
    item = tk.Frame(
        status_panel,
        background=PANEL,
    )

    item.grid(
        row=0,
        column=index,
        sticky="ew",
        padx=6,
        pady=4,
    )

    status_panel.grid_columnconfigure(
        index,
        weight=1,
    )

    tk.Label(
        item,
        text=label_text,
        background=PANEL,
        foreground=ACCENT,
        font=("Sans", 10, "bold"),
    ).pack()

    tk.Label(
        item,
        textvariable=variable,
        background=PANEL,
        foreground=TEXT,
        font=("Sans", 9),
    ).pack(
        pady=(1, 0),
    )


# =========================================================
# DASHBOARD BUTTONS
# =========================================================

create_section(
    dashboard_container,
    "SYSTEM",
    [
        ("System Info", "system"),
        ("Doctor", "doctor"),
        ("Distro", "distro"),
        ("Settings", "settings"),
    ],
)

create_section(
    dashboard_container,
    "SECURITY",
    [
        ("Firewall Status", "firewall status"),
        ("Enable Firewall", "enable firewall"),
        (
            "Disable Firewall",
            "disable firewall",
            "Danger.TButton",
        ),
        ("Health Check", "health"),
        ("VPN Status", "vpn status"),
        ("Tailscale", "tailscale status"),
        ("Network Scan", "network scan"),
        ("Check Updates", "check updates"),
    ],
)

create_section(
    dashboard_container,
    "FILES",
    [
        ("File Manager", "files"),
        ("List Home", "list ~"),
    ],
)

create_section(
    dashboard_container,
    "ASSISTANT",
    [
        ("Memory", "memories"),
        ("Travel Mode", "travel mode"),
        ("Translator", "help translator"),
        ("Help", "help"),
        ("About", "about"),
        ("News", "news"),
        ("Version", "version"),
    ],
)


# =========================================================
# OUTPUT PANEL
# =========================================================

output_frame = ttk.Frame(
    root,
    style="Panel.TFrame",
)

output_frame.grid(
    row=2,
    column=0,
    sticky="nsew",
    padx=18,
    pady=(4, 4),
)

output_frame.grid_rowconfigure(
    0,
    weight=1,
)

output_frame.grid_columnconfigure(
    0,
    weight=1,
)

output_box = scrolledtext.ScrolledText(
    output_frame,
    wrap=tk.WORD,
    font=("Sans", 11),
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

output_box.configure(
    state="disabled",
)


# =========================================================
# COMMAND BAR
# =========================================================

command_frame = tk.Frame(
    root,
    background=BACKGROUND,
)

command_frame.grid(
    row=3,
    column=0,
    sticky="ew",
    padx=18,
    pady=(4, 10),
)

command_frame.grid_columnconfigure(
    0,
    weight=1,
)

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
    ipady=7,
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


# =========================================================
# STARTUP
# =========================================================

write_output(
    f"Hello. I'm Sounix {SOUNIX_VERSION}.\n"
    "I'm a cybersecurity-focused, multipurpose Linux assistant.\n"
    "I'm still under active development by AdmiralChimken.\n\n"
    "Enter a command below or choose a dashboard action.\n\n"
)

command_entry.focus_set()

root.after(
    1000,
    check_updates_on_startup,
)

root.mainloop()
