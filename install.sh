#!/usr/bin/env bash
set -e

# ----------------------------
# Run from script directory
# ----------------------------
cd "$(dirname "$0")"

# ----------------------------
# Create virtual environment
# ----------------------------
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# ----------------------------
# Activate and install dependencies
# ----------------------------
echo "Installing dependencies..."
# Upgrade pip first
"$PWD/venv/bin/python" -m pip install --upgrade pip
"$PWD/venv/bin/python" -m pip install -r requirements.txt

echo
echo "Installation complete!"
echo "Use ./start.sh to launch the app."
