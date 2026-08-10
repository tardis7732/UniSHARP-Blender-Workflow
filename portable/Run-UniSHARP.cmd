@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Setup-UniSHARP.ps1" -Launch
if errorlevel 1 (
    echo.
    echo Setup did not complete. Read GPU-Setup-Guide.md, then run this file again.
    pause
)
