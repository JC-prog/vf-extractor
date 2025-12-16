@echo off
cd /d "%~dp0"

:: ----------------------------
:: Create virtual environment
:: ----------------------------
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

:: ----------------------------
:: Install dependencies
:: ----------------------------
echo Installing dependencies...
venv\Scripts\python.exe -m pip install --upgrade pip
venv\Scripts\python.exe -m pip install -r requirements.txt

echo Installation complete!
echo Use start.bat to launch the app.
pause
