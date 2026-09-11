@echo off
title NeuroScan AI - Full Application Launcher
cd /d "%~dp0"
echo ============================================================
echo         NEUROSCAN AI - ONE-CLICK APPLICATION LAUNCHER
echo ============================================================
echo.

:: 1. Launch Backend API in its own window
echo [1/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "NeuroScan AI - Backend API (Port 8000)" cmd /k call "%~dp0start_backend.bat"

:: Wait 3 seconds for model and API to load
timeout /t 3 /nobreak >nul

:: 2. Launch Frontend UI in its own window
echo [2/3] Starting Next.js Frontend on http://localhost:3000 ...
start "NeuroScan AI - Frontend (Port 3000)" cmd /k call "%~dp0start_frontend.bat"

:: Wait 2 seconds
timeout /t 2 /nobreak >nul

:: 3. Launch default browser
echo [3/3] Opening NeuroScan AI in your web browser...
start http://localhost:3000

echo.
echo ============================================================
echo   NeuroScan AI is now actively running!
echo   - Web App UI:  http://localhost:3000
echo   - Backend API: http://127.0.0.1:8000
echo   - API Docs:    http://127.0.0.1:8000/docs
echo ============================================================
echo.
echo Both servers are running in separate background windows.
echo To stop the application, simply close those terminal windows.
echo.
echo Press any key to close this launcher window.
pause >nul
