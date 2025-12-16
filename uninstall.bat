@echo off
cd /d "%~dp0"

if exist "venv" (
    echo Removing virtual environment...
    rmdir /s /q venv
) else (
    echo No virtual environment found.
)

echo Uninstallation complete!
pause
