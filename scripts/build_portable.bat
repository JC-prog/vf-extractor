@echo off
setlocal enabledelayedexpansion

REM ============================================================
REM build_portable.bat
REM
REM Builds a fully self-contained portable folder in dist\
REM that runs on Windows PCs without any installation.
REM
REM Requirements:
REM   - Run on an internet-connected machine
REM   - Python 3.12 must be available (for the embeddable download)
REM   - models\ must already be populated (run download_models.py first)
REM
REM Output: dist\  (~1.4 GB)
REM   Users copy dist\ to the target PC and double-click run.bat
REM ============================================================

REM Resolve project root regardless of where the script is called from
pushd "%~dp0.."
set "ROOT=%CD%"
popd
set "DIST=%ROOT%\dist"
set "PY_VERSION=3.12.10"
set "PY_ZIP=python-%PY_VERSION%-embed-amd64.zip"
set "PY_URL=https://www.python.org/ftp/python/%PY_VERSION%/%PY_ZIP%"

echo.
echo === vf-extractor Portable Builder ===
echo Project root: %ROOT%
echo Output:       %DIST%
echo.

REM --- Check models/ exists and is not empty ---
if not exist "%ROOT%\models\" (
    echo ERROR: models\ directory not found.
    echo Run "python scripts\download_models.py" first to pre-download PaddleOCR models.
    pause
    exit /b 1
)

REM --- Clean and create dist ---
if exist "%DIST%" (
    echo Removing existing dist\...
    rmdir /s /q "%DIST%"
)
mkdir "%DIST%"

REM ---- Step 1: Download Python embeddable ----
echo [1/6] Downloading Python %PY_VERSION% embeddable...
curl -L -o "%DIST%\%PY_ZIP%" "%PY_URL%"
if errorlevel 1 (
    echo.
    echo ERROR: Failed to download Python embeddable from:
    echo   %PY_URL%
    echo Check your internet connection and try again.
    pause
    exit /b 1
)

mkdir "%DIST%\python"
tar -xf "%DIST%\%PY_ZIP%" -C "%DIST%\python"
if errorlevel 1 (
    echo ERROR: Failed to extract Python embeddable zip.
    pause
    exit /b 1
)
del "%DIST%\%PY_ZIP%"

REM ---- Step 2: Enable site-packages in embeddable Python ----
echo [2/6] Configuring embeddable Python...
REM Uncomment "import site" in the ._pth file so pip-installed packages are found
set "PTH_FILE=%DIST%\python\python312._pth"
if not exist "%PTH_FILE%" (
    echo ERROR: Expected file not found: %PTH_FILE%
    echo The Python embeddable zip may be corrupt or the wrong version.
    pause
    exit /b 1
)
powershell -Command "(Get-Content '%PTH_FILE%') -replace '#import site', 'import site' | Set-Content '%PTH_FILE%'"

REM ---- Step 3: Install pip into embeddable Python ----
echo [3/6] Installing pip...
curl -L -o "%DIST%\get-pip.py" https://bootstrap.pypa.io/get-pip.py
if errorlevel 1 (
    echo ERROR: Failed to download get-pip.py.
    pause
    exit /b 1
)
"%DIST%\python\python.exe" "%DIST%\get-pip.py" --no-warn-script-location
del "%DIST%\get-pip.py"

REM ---- Step 4: Install all dependencies ----
echo [4/6] Installing Python packages (this will take a while)...

REM Normalize requirements.txt to UTF-8 (guards against editors saving as UTF-16)
powershell -Command ^
    "$raw = [System.IO.File]::ReadAllBytes('%ROOT%\requirements.txt');" ^
    "$text = if ($raw[1] -eq 0) { [System.Text.Encoding]::Unicode.GetString($raw) } else { [System.Text.Encoding]::UTF8.GetString($raw) };" ^
    "[System.IO.File]::WriteAllText('%DIST%\requirements.txt', $text, [System.Text.UTF8Encoding]::new($false))"

"%DIST%\python\python.exe" -m pip install -r "%DIST%\requirements.txt" ^
    --no-warn-script-location ^
    --no-cache-dir
if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed.
    echo Check the output above for details.
    pause
    exit /b 1
)

REM Install vfextractor package from local source
"%DIST%\python\python.exe" -m pip install "%ROOT%" --no-warn-script-location --no-deps

REM ---- Step 5: Copy app source and assets ----
echo [5/6] Copying application files...
xcopy /E /I /Q "%ROOT%\app"         "%DIST%\app"
xcopy /E /I /Q "%ROOT%\vfextractor" "%DIST%\vfextractor"
xcopy /E /I /Q "%ROOT%\models"      "%DIST%\models"
xcopy /E /I /Q "%ROOT%\.streamlit"  "%DIST%\.streamlit"

REM ---- Step 6: Write launcher ----
echo [6/6] Writing launcher...
(
    echo @echo off
    echo cd /d "%%~dp0"
    echo set "VF_MODELS_DIR=%%~dp0models"
    echo set "PADDLE_PDX_CACHE_HOME=%%~dp0models\paddlex"
    echo set "PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK=True"
    echo python\python.exe -m streamlit run app\app.py --server.port 8501 --server.headless false
    echo pause
) > "%DIST%\run.bat"

echo.
echo === Build complete! ===
echo Portable app is in: %DIST%
echo.
echo To distribute: copy the entire dist\ folder to the target PC.
echo To run: double-click dist\run.bat
echo.
pause
