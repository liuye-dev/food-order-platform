#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

echo "[1/4] Installing Python dependencies..."
uv sync

echo "[2/4] Preparing SQLite database..."
uv run python backend/manage.py migrate

echo "[3/4] Loading demo data..."
uv run python backend/manage.py loaddata demo_data

echo "[4/4] Starting backend and frontend..."
uv run python backend/manage.py runserver &
BACKEND_PID=$!

(
  cd "$PROJECT_DIR/frontend"
  npm install
  npm run dev
) &
FRONTEND_PID=$!

echo
echo "Demo is starting."
echo "Frontend: http://localhost:5173"
echo "Backend:  http://localhost:8000/api/health/"
echo
echo "Press Ctrl+C to stop both services."

wait
