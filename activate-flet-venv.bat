@echo off
echo ========================================
echo   Auto-Activating FletV2 Environment
echo ========================================
echo.

REM Change to the project directory
cd /d "%~dp0"

echo Activating flet_venv environment...
call "flet_venv\Scripts\activate.bat"

echo.
echo ✓ FletV2 environment is now active!
echo ✓ Python interpreter: %VIRTUAL_ENV%\Scripts\python.exe
echo ✓ Ready for development
echo.

REM Keep the window open if run directly
if "%1"=="" (
    echo Press any key to continue or close this window...
    pause >nul
)