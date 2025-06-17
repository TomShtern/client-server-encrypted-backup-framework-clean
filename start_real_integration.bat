@echo off
echo =======================================================
echo REAL ENCRYPTED BACKUP INTEGRATION SYSTEM
echo =======================================================
echo.

echo Installing dependencies...
pip install -r requirements_integration.txt

echo.
echo Checking system components...

if exist "client\EncryptedBackupClient.exe" (
    echo ✅ C++ Client: Found
) else (
    echo ❌ C++ Client: NOT FOUND
    echo    Please run build.bat first to compile the client
    pause
    exit /b 1
)

if exist "server\server.py" (
    echo ✅ Backup Server: Found
) else (
    echo ❌ Backup Server: NOT FOUND
    pause
    exit /b 1
)

if not exist "server\received_files" (
    echo Creating received_files directory...
    mkdir "server\received_files"
)

echo.
echo =======================================================
echo STARTING REAL INTEGRATION SERVER
echo =======================================================
echo.
echo Web Interface: http://localhost:5000
echo.
echo IMPORTANT: Make sure the Python backup server is running!
echo           Run "python server\server.py" in another terminal
echo.

python integration_web_server.py

pause
