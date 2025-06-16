@echo off
REM Start Complete CyberBackup System with HTML Client Support
echo ==========================================
echo CyberBackup Pro - Complete System Startup
echo ==========================================
echo.
echo This will start:
echo 1. Python Backup Server (port 1256)
echo 2. Web API Backend (port 9090) 
echo 3. HTML Client GUI (browser)
echo.

REM Check if executables exist
if not exist "client\SimpleWebServer.exe" (
    echo ERROR: SimpleWebServer.exe not found!
    echo Please run build.bat first.
    pause
    exit /b 1
)

if not exist "server\server.py" (
    echo ERROR: server.py not found!
    pause
    exit /b 1
)

echo Starting Python Backup Server...
start "Backup Server" cmd /k "cd server && python server.py"

timeout /t 3 /nobreak > nul

echo Starting Simple Web Server...
start "Simple Web Server" cmd /k "cd client && SimpleWebServer.exe"

timeout /t 2 /nobreak > nul

echo Opening HTML Client...
start "" "src\client\NewGUIforClient.html"

echo.
echo ==========================================
echo System Started Successfully!
echo ==========================================
echo.
echo - Backup Server: Running on port 1256
echo - Simple Web Server: Running on port 9090  
echo - HTML Client: Opened in browser
echo.
echo To stop the system:
echo 1. Close the HTML client browser tab
echo 2. Close the "Simple Web Server" window
echo 3. Close the "Backup Server" window
echo.
echo Press any key to exit this launcher...
pause > nul
