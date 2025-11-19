@echo off
REM CyberBackup UTF-8 Launcher
REM This script sets UTF-8 encoding ONLY for this backup system session

echo ================================================
echo  CyberBackup UTF-8 Launcher
echo ================================================
echo Setting up UTF-8 environment for this session...

REM Set environment variables for UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Try to set console to UTF-8 (will revert when window closes)
chcp 65001 >nul 2>&1
if errorlevel 1 (
    echo Note: Could not change console encoding
) else (
    echo Console encoding set to UTF-8 for this session
)

echo.
echo Starting CyberBackup system...
echo.

REM Launch the fixed launcher with UTF-8 environment
python scripts\fixed_launcher.py

echo.
echo ================================================
echo  CyberBackup session complete
echo  Console encoding will revert when you close this window
echo ================================================
pause