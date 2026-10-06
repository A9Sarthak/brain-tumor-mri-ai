@echo off
title NeuroScan AI - Download Dataset
cd /d "%~dp0"
echo ============================================================
echo   NEUROSCAN AI - DATASET DOWNLOADER
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\download_dataset.py
) else (
    python scripts\download_dataset.py
)

echo.
pause
