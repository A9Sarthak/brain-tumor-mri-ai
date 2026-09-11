@echo off
title NeuroScan AI - Next.js Frontend
cd /d "%~dp0frontend"
echo ============================================================
echo   NEUROSCAN AI - Starting Next.js Web Frontend
echo ============================================================
echo.

:: Auto-detect Node.js in PATH or common portable directories
where node >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Users\darsh\node-v20.18.0-win-x64" (
        set "PATH=C:\Users\darsh\node-v20.18.0-win-x64;%PATH%"
    ) else if exist "%USERPROFILE%\node-v20.18.0-win-x64" (
        set "PATH=%USERPROFILE%\node-v20.18.0-win-x64;%PATH%"
    ) else (
        echo [ERROR] Node.js not found! Please ensure Node.js is installed.
        pause
        exit /b 1
    )
)

echo Starting server on http://localhost:3000 ...
npm run start -- -p 3000
if %errorlevel% neq 0 (
    echo Production bundle not ready, starting in dev mode...
    npm run dev
)
