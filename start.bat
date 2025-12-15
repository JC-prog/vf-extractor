@echo off
SETLOCAL

:: ----------------------------
:: Configurable ports
:: ----------------------------
set STREAMLIT_PORT=8501

:: ----------------------------
:: Activate virtual environment
:: ----------------------------
:: call venv\Scripts\activate.bat

:: ----------------------------
:: Check if port is free
:: ----------------------------
netstat -ano | findstr :%STREAMLIT_PORT%
IF %ERRORLEVEL%==0 (
    echo Port %STREAMLIT_PORT% is in use. Please free it first.
    exit /b 1
)

:: ----------------------------
:: Start Streamlit app
:: ----------------------------
echo Starting Streamlit app at http://127.0.0.1:%STREAMLIT_PORT%...
:: start "Streamlit" cmd /k "streamlit run app\app.py --server.port %STREAMLIT_PORT%"

:: ----------------------------
:: Open browser
:: ----------------------------
:: start "" http://127.0.0.1:%STREAMLIT_PORT%

echo Press Ctrl+C to stop servers. Close the command windows to exit.

ENDLOCAL
