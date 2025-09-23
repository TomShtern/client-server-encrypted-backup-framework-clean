@echo off
echo ========================================
echo   Server GUI Launcher
echo ========================================
echo.

cd /d "C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework"

echo Setting up environment...
set "PYTHONPATH=C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework"

echo Starting Server GUI...
echo.

"flet_venv\Scripts\python.exe" "python_server\server_gui\ServerGUI.py"

echo.
echo Server GUI has closed.
pause
