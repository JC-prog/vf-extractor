#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

PORT=8501
VENV_PY="venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: virtualenv not found at $VENV_PY"
  echo "Did you create the venv?"
  exit 1
fi

echo "Starting Streamlit at http://127.0.0.1:$PORT"
echo "Close this terminal to stop the app"
echo

"$VENV_PY" -m streamlit run app/app.py --server.port "$PORT"
