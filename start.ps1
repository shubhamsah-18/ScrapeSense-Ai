# ScrapSense AI - PowerShell Startup Script
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ♻️  ScrapSense AI - Smart Waste & Scrap Resale Platform" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$pythonExe = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $pythonExe = ".\.venv\Scripts\python.exe"
    Write-Host "[*] Using project virtual environment: .venv" -ForegroundColor Cyan
} elseif (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Python was not found in your PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
}

Write-Host "[*] Python runtime: $pythonExe" -ForegroundColor Yellow
Write-Host "[*] Verifying backend dependencies..." -ForegroundColor Yellow
& $pythonExe -m pip install -r backend/requirements.txt --quiet --disable-pip-version-check

Write-Host "[*] Launching ScrapSense AI Live Server & Backend..." -ForegroundColor Green
& $pythonExe run.py
