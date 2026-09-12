@echo off
title NeuroScan AI - Backend Server
cd /d "%~dp0"
echo ============================================================
echo   NEUROSCAN AI - Starting FastAPI Backend Server
echo ============================================================
echo.
if exist ".venv\Scripts\uvicorn.exe" (
    ".venv\Scripts\uvicorn.exe" backend.main:app --host 127.0.0.1 --port 8000
) else (
    echo [ERROR] Python virtual environment .venv not found!
    echo Please ensure .venv is installed in the project root.
    pause
)
