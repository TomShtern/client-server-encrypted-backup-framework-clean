@echo off

REM Kill any existing client processes
taskkill /F /IM EncryptedBackupClient.exe 2>nul

REM Simplified build and run script

REM Change to project root directory
cd /d "%~dp0"

REM Configure CMake
call scripts\configure_cmake.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: CMake configuration failed!
    pause
    exit /b 1
)

REM Build C++ client
cmake --build build --config Release
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: C++ client build failed!
    pause
    exit /b 1
)

REM Run the client
build\Release\EncryptedBackupClient.exe
