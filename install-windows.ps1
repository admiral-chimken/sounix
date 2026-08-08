Write-Host ""
Write-Host "====================================="
Write-Host "        SOUNIX WINDOWS INSTALLER"
Write-Host "====================================="
Write-Host ""

# Make sure Python exists
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python was not found."
    Write-Host ""
    Write-Host "Install Python from:"
    Write-Host "https://www.python.org/downloads/windows/"
    Write-Host ""
    Write-Host "Make sure 'Add Python to PATH' is enabled during installation."
    exit 1
}

Write-Host "Python detected."

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host ""
    Write-Host "Creating Sounix virtual environment..."
    python -m venv venv
}
else {
    Write-Host "Virtual environment already exists."
}

$PythonExe = ".\venv\Scripts\python.exe"
$PipExe = ".\venv\Scripts\pip.exe"

# Upgrade pip
Write-Host ""
Write-Host "Updating pip..."
& $PythonExe -m pip install --upgrade pip

# Install requirements
if (Test-Path "requirements.txt") {
    Write-Host ""
    Write-Host "Installing Sounix dependencies..."
    & $PipExe install -r requirements.txt
}
else {
    Write-Host ""
    Write-Host "Warning: requirements.txt was not found."
}

Write-Host ""
Write-Host "====================================="
Write-Host "       SOUNIX INSTALL COMPLETE"
Write-Host "====================================="
Write-Host ""
Write-Host "To launch Sounix, run:"
Write-Host ""
Write-Host ".\sounix-windows.ps1"
Write-Host ""

