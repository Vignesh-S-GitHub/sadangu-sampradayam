Set-Location "$PSScriptRoot/../mobile"
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -e .
flet run src/main.py
