$PythonExe = ".\venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Host "Sounix is not installed yet."
    Write-Host "Run:"
    Write-Host ".\install-windows.ps1"
    exit 1
}

& $PythonExe ".\app\gui.py"
