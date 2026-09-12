Set-Location "$PSScriptRoot/../backend"
if (-not (Test-Path .venv)) { python -m venv .venv }
& .\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn app.main:app --reload
