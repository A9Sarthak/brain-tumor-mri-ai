@echo off
title NeuroScan AI - View Processed Data
echo ======================================================================
echo Launching Brain Tumor MRI Processed Data Inspector...
echo ======================================================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\view_processed_data.py
) else (
    python scripts\view_processed_data.py
)
pause
