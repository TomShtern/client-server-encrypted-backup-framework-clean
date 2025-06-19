@echo off
echo =====================================================================
echo   🚀 CYBERBACKUP 3.0 - COMPLETE REAL INTEGRATION SYSTEM
echo =====================================================================
echo.

echo Cleaning up any existing servers...
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *server*" >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *API*" >nul 2>&1
timeout /t 2 /nobreak >nul

echo Installing Python dependencies...
pip install flask flask-cors psutil requests

echo.
echo Checking system components...

:: Check C++ client
if exist "client\EncryptedBackupClient.exe" (
    echo ✅ C++ Client: Found
) else (
    echo ❌ C++ Client: NOT FOUND
    echo    Please run build.bat first to compile the client
    pause
    exit /b 1
)

:: Check HTML client
if exist "src\client\NewGUIforClient.html" (
    echo ✅ HTML Client: Found
) else (
    echo ❌ HTML Client: NOT FOUND
    pause
    exit /b 1
)

:: Check backup server
if exist "server\server.py" (
    echo ✅ Backup Server: Found
) else (
    echo ❌ Backup Server: NOT FOUND
    pause
    exit /b 1
)

:: Create received_files directory if needed
if not exist "server\received_files" (
    echo Creating received_files directory...
    mkdir "server\received_files"
)

echo.
echo =====================================================================
echo   🌟 STARTING CYBERBACKUP 3.0 REAL INTEGRATION SYSTEM
echo =====================================================================
echo.
echo This will start:
echo   1. Python Backup Server (port 1256) - REAL backup processing
echo   2. Server GUI - Visual server management interface
echo   3. CyberBackup 3.0 API Server (port 9090) - API backend
echo   4. CyberBackup 3.0 HTML GUI - Modern web interface
echo.
echo IMPORTANT: Keep this window open - it manages all servers!
echo           Files will be ACTUALLY transferred to received_files!
echo.

:: Start backup server in background
echo Starting Python backup server...
start "Backup Server" cmd /c "python server\server.py"

:: Wait a moment for server to start
timeout /t 3 /nobreak >nul

:: Start server GUI
echo Starting Server GUI...
start "Server GUI" cmd /c "python server\ServerGUI.py"

:: Wait a moment for GUI to start
timeout /t 2 /nobreak >nul

:: Start API server in background
echo Starting CyberBackup 3.0 API server...
start "API Server" cmd /c "python cyberbackup_api_server.py"

:: Wait a moment for API server to start
timeout /t 3 /nobreak >nul

:: Open the GUI in default browser
echo Opening CyberBackup 3.0 GUI...
start "" "http://localhost:9090"

echo.
echo =====================================================================
echo   ✅ CYBERBACKUP 3.0 REAL INTEGRATION SYSTEM RUNNING
echo =====================================================================
echo.
echo   🌐 CyberBackup 3.0 GUI: http://localhost:9090
echo   📡 API Server: http://localhost:9090/api/status
echo   🗄️  Backup Server: localhost:1256
echo   📁 Received Files: server\received_files
echo.
echo   The system is now ready for REAL encrypted backups!
echo   Files uploaded will be ACTUALLY transferred and saved!
echo.
echo   Press any key to shut down all servers...
pause >nul

echo.
echo Shutting down servers...
taskkill /f /fi "windowtitle eq Backup Server*" >nul 2>&1
taskkill /f /fi "windowtitle eq Server GUI*" >nul 2>&1
taskkill /f /fi "windowtitle eq API Server*" >nul 2>&1

echo ✅ All servers stopped.
echo Thank you for using CyberBackup 3.0!
pause
