#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-sadangu-sampradayam}"
VISIBILITY="${2:---private}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required: https://cli.github.com/"
  exit 1
fi

git init -b main 2>/dev/null || true
git add .
git commit -m "Initial Sadangu Sampradayam V1" || true
gh repo create "$REPO_NAME" "$VISIBILITY" --source=. --remote=origin --push
