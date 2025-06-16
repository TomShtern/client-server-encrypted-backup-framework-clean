@echo off
REM Start Simple Web Server for HTML Client
echo Starting CyberBackup Simple Web Server...
echo.
echo This server provides the API endpoints for the HTML client.
echo The HTML client should be available at: file:///[path-to-project]/src/client/NewGUIforClient.html
echo API Server will run on: http://127.0.0.1:9090
echo.
echo Press Ctrl+C to stop the server
echo.

cd client
if exist "SimpleWebServer.exe" (
    echo Starting Simple Web Server...
    SimpleWebServer.exe
) else (
    echo ERROR: SimpleWebServer.exe not found!
    echo Please run build.bat first to compile the web server.
    echo.
    pause
)
