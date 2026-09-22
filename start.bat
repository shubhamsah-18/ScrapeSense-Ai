@echo off
title ScrapSense AI - Smart Scrap Valuation Platform
color 0A

echo ============================================================
echo   ScrapSense AI - Smart Waste & Scrap Resale Platform
echo ============================================================
echo.

set PYTHON_EXE=python
if exist .venv\Scripts\python.exe (
    set PYTHON_EXE=.venv\Scripts\python.exe
    echo [*] Using project virtual environment: .venv
) else (
    %PYTHON_EXE% --version >nul 2>&1
    if errorlevel 1 (
        echo [!] Python was not found in your PATH.
        echo Please install Python 3.9+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

echo [*] Python runtime: %PYTHON_EXE%
echo [*] Checking dependencies...
%PYTHON_EXE% -m pip install -r backend\requirements.txt --quiet --disable-pip-version-check

echo.
echo [*] Launching ScrapSense AI Live Server ^& Backend...
%PYTHON_EXE% run.py

pause
