@echo off
:: ScrapSense AI - Windows Firewall Port Opener for Mobile Access
title ScrapSense AI - Allow Mobile Access (Firewall)
color 0B

echo ============================================================
echo   ScrapSense AI - Mobile Network Access Setup
echo ============================================================
echo.
echo Opening Windows Firewall inbound ports for:
echo   - Frontend Live Server : Port 5500 (TCP)
echo   - FastAPI Backend      : Port 8000 (TCP)
echo.

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

echo [*] Adding Inbound Rule for Port 5500...
netsh advfirewall firewall delete rule name="ScrapSense AI Frontend (5500)" >nul 2>&1
netsh advfirewall firewall add rule name="ScrapSense AI Frontend (5500)" dir=in action=allow protocol=TCP localport=5500 profile=any >nul 2>&1

echo [*] Adding Inbound Rule for Port 8000...
netsh advfirewall firewall delete rule name="ScrapSense AI Backend (8000)" >nul 2>&1
netsh advfirewall firewall add rule name="ScrapSense AI Backend (8000)" dir=in action=allow protocol=TCP localport=8000 profile=any >nul 2>&1

echo.
echo ============================================================
echo [SUCCESS] Windows Firewall is configured!
echo Mobile phones on your Wi-Fi can now connect without blockage.
echo ============================================================
echo.
pause
