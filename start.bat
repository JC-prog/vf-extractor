@echo off
cd /d "%~dp0"
SETLOCAL

set PY=venv\Scripts\python.exe
set PORT=8501

IF NOT EXIST "%PY%" (
    echo ERROR: venv not found
    pause
    exit /b 1
)

echo Starting Streamlit at http://127.0.0.1:%PORT%
echo Close this window to stop the app.
echo.

"%PY%" -m streamlit run app\app.py --server.port %PORT%
