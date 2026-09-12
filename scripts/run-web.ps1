$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting Sadangu Sampradayam API..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; if (!(Test-Path .venv)) { py -m venv .venv }; .\.venv\Scripts\Activate.ps1; pip install -e .; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

Write-Host "Starting Flet web app..."
Set-Location "$root\mobile"
if (!(Test-Path .venv)) { py -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -e .
$env:SADANGU_API_URL = "http://127.0.0.1:8000"
flet run --web --port 8550 src/main.py
