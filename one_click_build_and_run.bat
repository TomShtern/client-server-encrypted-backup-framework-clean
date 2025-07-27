@echo off
REM ========================================================================
REM   ONE-CLICK BUILD AND RUN - CyberBackup 3.0 (ROOT WRAPPER)
REM ========================================================================
REM
REM This is a simple wrapper that calls the comprehensive build script.
REM It handles the complete build, configuration, and launch process.
REM
REM Author: Auto-generated for CyberBackup 3.0
REM ========================================================================

echo.
echo ========================================================================
echo   [ROCKET] ONE-CLICK BUILD AND RUN - CyberBackup 3.0
echo ========================================================================
echo.
echo Launching comprehensive build and run process...
echo.

REM Call the comprehensive script
call "scripts\build\one_click_build_and_run.bat"

REM Pass through the exit code
exit /b %ERRORLEVEL%