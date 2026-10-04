#!/usr/bin/env bash
# Linux/macOS setup: venv + backend deps + frontend build.
set -e
cd "$(dirname "$0")/.."

echo "[1/4] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "[2/4] Installing backend dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt

echo "[3/4] Installing frontend dependencies..."
cd frontend && npm install

echo "[4/4] Building production frontend..."
npm run build
cd ..

echo "Setup complete."
echo "  scripts/start_backend.sh   - starts app at http://localhost:8000"
echo "  scripts/run_tests.sh       - runs all automated tests"
