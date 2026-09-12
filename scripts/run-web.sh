#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

(cd "$ROOT/backend" && python -m venv .venv && . .venv/bin/activate && pip install -e . && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000) &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT

cd "$ROOT/mobile"
python -m venv .venv
. .venv/bin/activate
pip install -e .
export SADANGU_API_URL=http://127.0.0.1:8000
flet run --web --port 8550 src/main.py
