#!/usr/bin/env bash

set -euo pipefail

APP_NAME="Sounix"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
APP_FILE="$PROJECT_DIR/app/gui.py"
LAUNCHER_FILE="$PROJECT_DIR/sounix"


show_header() {
    echo "=================================="
    echo "       SOUNIX SMART INSTALLER"
    echo "=================================="
    echo
}


run_admin() {
    if [ "$(id -u)" -eq 0 ]; then
        "$@"
    elif command -v sudo >/dev/null 2>&1; then
        sudo "$@"
    else
        echo "Sounix: Administrator access is required."
        echo "Install sudo or run this installer as root."
        exit 1
    fi
}


detect_system() {
    OS_NAME="$(uname -s)"

    if [ "$OS_NAME" != "Linux" ]; then
        echo "Sounix currently supports Linux only."
        echo "Detected operating system: $OS_NAME"
        echo
        echo "Windows and macOS support are planned."
        exit 1
    fi

    if [ ! -f /etc/os-release ]; then
        echo "Sounix could not identify this Linux distribution."
        exit 1
    fi

    # Load ID, NAME, ID_LIKE, and related distribution information.
    . /etc/os-release

    DISTRO_ID="${ID:-unknown}"
    DISTRO_NAME="${PRETTY_NAME:-${NAME:-Unknown Linux}}"
    DISTRO_LIKE="${ID_LIKE:-}"

    echo "Detected operating system: Linux"
    echo "Detected distribution: $DISTRO_NAME"
    echo
}


install_system_dependencies() {
    echo "Checking system dependencies..."

    if command -v pacman >/dev/null 2>&1; then
        echo "Package manager: pacman"
        run_admin pacman -S --needed --noconfirm \
            python \
            python-pip \
            tk \
            git

    elif command -v apt-get >/dev/null 2>&1; then
        echo "Package manager: apt"
        run_admin apt-get update
        run_admin apt-get install -y \
            python3 \
            python3-venv \
            python3-pip \
            python3-tk \
            git

    elif command -v dnf >/dev/null 2>&1; then
        echo "Package manager: dnf"
        run_admin dnf install -y \
            python3 \
            python3-pip \
            python3-tkinter \
            git

    else
        echo
        echo "Sounix does not currently support this package manager."
        echo "Detected distribution: $DISTRO_NAME"
        echo
        echo "Supported package managers:"
        echo "  pacman — Arch Linux"
        echo "  apt    — Kali, Debian, Ubuntu"
        echo "  dnf    — Fedora"
        exit 1
    fi

    echo "System dependencies are ready."
    echo
}


find_python() {
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_COMMAND="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON_COMMAND="python"
    else
        echo "Sounix: Python was not found after installation."
        exit 1
    fi

    echo "Python detected: $($PYTHON_COMMAND --version)"
    echo
}


create_environment() {
    echo "Creating Python virtual environment..."

    if [ ! -d "$VENV_DIR" ]; then
        "$PYTHON_COMMAND" -m venv "$VENV_DIR"
    else
        echo "Existing virtual environment found."
    fi

    VENV_PYTHON="$VENV_DIR/bin/python"
    VENV_PIP="$VENV_DIR/bin/pip"

    "$VENV_PYTHON" -m pip install --upgrade pip

    if [ -f "$REQUIREMENTS_FILE" ]; then
        echo "Installing Python requirements..."
        "$VENV_PIP" install -r "$REQUIREMENTS_FILE"
    else
        echo "No requirements.txt file found; skipping Python packages."
    fi

    echo
}


verify_installation() {
    echo "Checking Sounix installation..."

    if [ ! -f "$APP_FILE" ]; then
        echo "Sounix: The application file was not found:"
        echo "$APP_FILE"
        exit 1
    fi

    "$VENV_PYTHON" -c "import tkinter"
    "$VENV_PYTHON" -m py_compile "$PROJECT_DIR/app/gui.py"
    "$VENV_PYTHON" -m py_compile "$PROJECT_DIR/app/ai.py"

    echo "Sounix passed its installation checks."
    echo
}


create_launcher() {
    echo "Creating Sounix launcher..."

    cat > "$LAUNCHER_FILE" <<EOF
#!/usr/bin/env bash

PROJECT_DIR="$PROJECT_DIR"
exec "\$PROJECT_DIR/venv/bin/python" "\$PROJECT_DIR/app/gui.py"
EOF

    chmod +x "$LAUNCHER_FILE"

    echo "Launcher created: $LAUNCHER_FILE"
    echo
}


finish_installation() {
    echo "=================================="
    echo "     SOUNIX INSTALLATION DONE"
    echo "=================================="
    echo
    echo "Start Sounix with:"
    echo
    echo "  cd \"$PROJECT_DIR\""
    echo "  ./sounix"
    echo
}


main() {
    show_header
    detect_system
    install_system_dependencies
    find_python
    create_environment
    verify_installation
    create_launcher
    finish_installation
}


main "$@"
