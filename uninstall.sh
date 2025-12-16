#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing virtual environment..."
    rm -rf venv
else
    echo "No virtual environment found."
fi

echo "Uninstallation complete!"
