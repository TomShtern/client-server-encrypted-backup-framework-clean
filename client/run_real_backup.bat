@echo off
REM Real backup integration script
echo Starting real backup operation...
echo.

REM Check if backup server is running
echo Checking if backup server is running on port 1256...
netstat -an | find "1256" > nul
if %ERRORLEVEL% neq 0 (
    echo ERROR: Backup server is not running on port 1256
    echo Please start the Python backup server first
    exit /b 1
)

echo Backup server is running - proceeding with backup...
echo.

REM Run the real C++ backup client
echo Executing EncryptedBackupClient.exe...
EncryptedBackupClient.exe

echo.
echo Backup operation completed.
echo Return code: %ERRORLEVEL%
