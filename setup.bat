@echo off
setlocal enabledelayedexpansion
title NeuroScan AI - Automatic Environment Setup
cd /d "%~dp0"

echo ============================================================
echo         NEUROSCAN AI - AUTOMATED PROJECT SETUP
echo ============================================================
echo.
echo This script will configure your system to run NeuroScan AI:
echo   1. Detect Python and create isolated virtual environment (.venv)
echo   2. Install all required AI/ML & Backend dependencies
echo   3. Detect Node.js and install Next.js frontend packages
echo   4. Build the production frontend bundle
echo.
echo ============================================================
echo.

:: -------------------------------------------------------------
:: Step 1: Detect Python
:: -------------------------------------------------------------
echo [1/5] Checking Python installation...
set "PY_CMD="

python --version >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>nul
    if %errorlevel% equ 0 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python was not found on your PATH!
    echo Please install Python 3.10 or 3.11 from:
    echo   https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PY_CMD% --version 2^>^&1') do echo Detected: %%v

:: -------------------------------------------------------------
:: Step 2: Create Python Virtual Environment (.venv)
:: -------------------------------------------------------------
echo.
echo [2/5] Setting up Python virtual environment (.venv)...
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment at .venv ...
    %PY_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Existing virtual environment found in .venv.
)

:: -------------------------------------------------------------
:: Step 3: Install Python Dependencies
:: -------------------------------------------------------------
echo.
echo [3/5] Installing Python dependencies (TensorFlow, FastAPI, OpenCV, etc.)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)
echo Python dependencies verified and up to date.

:: -------------------------------------------------------------
:: Step 4: Detect Node.js & Setup Frontend
:: -------------------------------------------------------------
echo.
echo [4/5] Checking Node.js and installing frontend packages...

where node >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Program Files\nodejs\node.exe" (
        set "PATH=C:\Program Files\nodejs;%PATH%"
    ) else if exist "%ProgramFiles%\nodejs\node.exe" (
        set "PATH=%ProgramFiles%\nodejs;%PATH%"
    ) else if exist "%LOCALAPPDATA%\Programs\node\nodejs\node.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\node\nodejs;%PATH%"
    ) else if exist "C:\Users\darsh\node-v20.18.0-win-x64" (
        set "PATH=C:\Users\darsh\node-v20.18.0-win-x64;%PATH%"
    ) else if exist "%USERPROFILE%\node-v20.18.0-win-x64" (
        set "PATH=%USERPROFILE%\node-v20.18.0-win-x64;%PATH%"
    )
)

where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was not found!
    echo Please install Node.js v18 or v20 LTS from:
    echo   https://nodejs.org/
    echo Once installed, rerun setup.bat.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node -v 2^>^&1') do echo Detected Node.js: %%v

cd /d "%~dp0frontend"
echo Installing npm packages...
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install frontend npm packages.
    cd /d "%~dp0"
    pause
    exit /b 1
)

echo Building Next.js production bundle...
call npm run build
if %errorlevel% neq 0 (
    echo [WARNING] Production build encountered an issue, but development mode will still work.
)
cd /d "%~dp0"

:: -------------------------------------------------------------
:: Step 5: Model Weights Verification
:: -------------------------------------------------------------
echo.
echo [5/5] Verifying AI Model weights...
if exist "models\best_efficientnet_model.keras" (
    echo AI model weights detected at: models\best_efficientnet_model.keras
) else (
    echo [NOTICE] Trained weights 'models\best_efficientnet_model.keras' not found.
    echo If you just cloned this repository, please place your trained
    echo 'best_efficientnet_model.keras' into the 'models\' directory.
)

echo.
echo ============================================================
echo         NEUROSCAN AI SETUP COMPLETED SUCCESSFULLY!
echo ============================================================
echo.
echo You can start the full application anytime by double-clicking:
echo   start.bat
echo.
set /p LAUNCH="Would you like to launch NeuroScan AI right now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    echo Launching NeuroScan AI...
    call "%~dp0start.bat"
) else (
    echo Setup finished. Press any key to exit.
    pause >nul
)
