#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
source .venv/bin/activate 2>/dev/null || true
exec python3 -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
