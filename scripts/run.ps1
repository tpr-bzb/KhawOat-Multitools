$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    throw "Missing virtual environment. Run scripts/setup.ps1 first."
}

Set-Location $ProjectRoot
& $VenvPython -m flet run main.py
