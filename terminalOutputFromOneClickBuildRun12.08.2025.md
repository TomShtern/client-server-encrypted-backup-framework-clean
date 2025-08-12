PS C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework> & C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\.venv\Scripts\Activate.ps1
(.venv) PS C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework> & C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\.venv\Scripts\python.exe c:/Users/tom7s/Desktopp/Claude_Folder_2/Client_Server_Encrypted_Backup_Framework/scripts/one_click_build_and_run.py
2025-08-12 12:36:50,663 - INFO - Starting CyberBackup 3.0 build and deployment process
2025-08-12 12:36:50,755 - INFO - Unicode console setup completed successfully
2025-08-12 12:36:50,756 - INFO - Emoji support detected: True

========================================================================
   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0
========================================================================

Starting complete build and deployment process...
This will configure, build, and launch the entire backup framework.

Working directory: c:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework


[12:36:50] [PHASE 0/7] Cleaning Up Existing Processes...
--------------------------------------------------
Cleaning up existing CyberBackup processes...

[WARNING] Error during process cleanup: invalid attr name 'connections'
No CyberBackup processes found running.

Checking for processes on port 9090...
Checking for processes on port 1256...
[OK] Process cleanup completed!


[12:36:50] [PHASE 1/7] Checking Prerequisites...
--------------------------------------------------
[OK] Python found: 3.13.5
[OK] CMake found: 4.0.3
[OK] Git found

Prerequisites check completed successfully!


[12:36:51] [PHASE 2/7] Configuring Build System...
--------------------------------------------------
Checking vcpkg dependencies...
[OK] All required vcpkg dependencies are present
Calling scripts\build\configure_cmake.bat for CMake + vcpkg setup...

Running: scripts\build\configure_cmake.bat

===============================================
 Configuring CMake for Portable Build System
===============================================
Current directory (project root expected): c:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework
[ERROR] Could not locate vcpkg directory. Aborting.

[OK] CMake configuration completed successfully!


[12:36:51] [PHASE 3/7] Building C++ Client...
--------------------------------------------------
Building EncryptedBackupClient.exe with CMake...
Command: cmake --build build --config Release

Running: cmake --build build --config Release

MSBuild version 17.14.14+a129329f1 for .NET Framework

  EncryptedBackupClient.vcxproj -> C:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\build\Release\EncryptedBackupClient.exe
[OK] C++ client found: build\Release\EncryptedBackupClient.exe

[OK] C++ client built successfully!
   Location: build\Release\EncryptedBackupClient.exe


[12:36:55] [PHASE 4/7] Setting up Python Environment...
--------------------------------------------------
Installing Python dependencies from requirements.txt...

Running: pip install -r requirements.txt

Requirement already satisfied: cryptography>=3.4.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 1)) (45.0.5)
Requirement already satisfied: pycryptodome>=3.15.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 2)) (3.23.0)
Requirement already satisfied: psutil>=5.8.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 3)) (7.0.0)
Requirement already satisfied: Flask>=2.0.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 4)) (3.1.1)
Requirement already satisfied: flask-cors>=6.0.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 5)) (6.0.1)
Requirement already satisfied: flask-socketio in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 6)) (5.5.1)
Requirement already satisfied: sentry-sdk in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 7)) (2.33.2)
Requirement already satisfied: watchdog>=2.1.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from -r requirements.txt (line 8)) (6.0.0)
Requirement already satisfied: cffi>=1.14 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from cryptography>=3.4.0->-r requirements.txt (line 1)) (1.17.1)
Requirement already satisfied: blinker>=1.9.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (1.9.0)
Requirement already satisfied: click>=8.1.3 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (8.2.1)
Requirement already satisfied: itsdangerous>=2.2.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (2.2.0)
Requirement already satisfied: jinja2>=3.1.2 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (3.1.6)
Requirement already satisfied: markupsafe>=2.1.1 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (3.0.2)
Requirement already satisfied: werkzeug>=3.1.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from Flask>=2.0.0->-r requirements.txt (line 4)) (3.1.3)
Requirement already satisfied: python-socketio>=5.12.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask-socketio->-r requirements.txt (line 6)) (5.13.0)
Requirement already satisfied: urllib3>=1.26.11 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from sentry-sdk->-r requirements.txt (line 7)) (2.5.0)
Requirement already satisfied: certifi in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from sentry-sdk->-r requirements.txt (line 7)) (2025.7.14)
Requirement already satisfied: pycparser in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from cffi>=1.14->cryptography>=3.4.0->-r requirements.txt (line 1)) (2.22)
Requirement already satisfied: colorama in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from click>=8.1.3->Flask>=2.0.0->-r requirements.txt (line 4)) (0.4.6)
Requirement already satisfied: bidict>=0.21.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from python-socketio>=5.12.0->flask-socketio->-r requirements.txt (line 6)) (0.23.1)
Requirement already satisfied: python-engineio>=4.11.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from python-socketio>=5.12.0->flask-socketio->-r requirements.txt (line 6)) (4.12.2)
Requirement already satisfied: simple-websocket>=0.10.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from python-engineio>=4.11.0->python-socketio>=5.12.0->flask-socketio->-r requirements.txt (line 6)) (1.1.0)
Requirement already satisfied: wsproto in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from simple-websocket>=0.10.0->python-engineio>=4.11.0->python-socketio>=5.12.0->flask-socketio->-r requirements.txt (line 6)) (1.2.0)
Requirement already satisfied: h11<1,>=0.9.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from wsproto->simple-websocket>=0.10.0->python-engineio>=4.11.0->python-socketio>=5.12.0->flask-socketio->-r requirements.txt (line 6)) (0.16.0)
[OK] Python dependencies installed successfully!
Installing additional dependencies...
Installing sentry-sdk...
Running: pip install sentry-sdk

Requirement already satisfied: sentry-sdk in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (2.33.2)
Requirement already satisfied: urllib3>=1.26.11 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from sentry-sdk) (2.5.0)
Requirement already satisfied: certifi in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from sentry-sdk) (2025.7.14)
[OK] sentry-sdk installed successfully
Installing flask-cors...
Running: pip install flask-cors

Requirement already satisfied: flask-cors in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (6.0.1)
Requirement already satisfied: flask>=0.9 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask-cors) (3.1.1)
Requirement already satisfied: Werkzeug>=0.7 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask-cors) (3.1.3)
Requirement already satisfied: blinker>=1.9.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask>=0.9->flask-cors) (1.9.0)
Requirement already satisfied: click>=8.1.3 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask>=0.9->flask-cors) (8.2.1)
Requirement already satisfied: itsdangerous>=2.2.0 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask>=0.9->flask-cors) (2.2.0)
Requirement already satisfied: jinja2>=3.1.2 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask>=0.9->flask-cors) (3.1.6)
Requirement already satisfied: markupsafe>=2.1.1 in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from flask>=0.9->flask-cors) (3.0.2)
Requirement already satisfied: colorama in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (from click>=8.1.3->flask>=0.9->flask-cors) (0.4.6)
[OK] flask-cors installed successfully
Installing watchdog...
Running: pip install watchdog

Requirement already satisfied: watchdog in c:\users\tom7s\desktopp\claude_folder_2\client_server_encrypted_backup_framework\.venv\lib\site-packages (6.0.0)
[OK] watchdog installed successfully


[12:37:05] [PHASE 5/7] Verifying Configuration...
--------------------------------------------------
[OK] RSA private key found
[OK] RSA public key found
[OK] transfer.info configuration found

[OK] Configuration verification completed!


[12:37:05] [PHASE 6/7] Launching Services...
--------------------------------------------------
Starting the complete CyberBackup 3.0 system...

Services that will be started:
   - Backup Server (Port 1256)
   - API Bridge Server (Port 9090)
   - Web GUI (Browser interface)

Starting Python Backup Server (python_server.server.server module)...
[INFO] AppMap detected - enabling execution recording
Command: appmap-python --record process python -m python_server.server.server
[GUI] Embedded Server GUI enabled (default)
Python Backup Server started with PID: 17104
[INFO] AppMap recording active - execution traces will be generated
       AppMap data will be saved when the server stops
Waiting for backup server to start listening...
  Attempt 1/30: Waiting for backup server...
  Attempt 2/30: Waiting for backup server...
  Attempt 3/30: Waiting for backup server...
  Attempt 4/30: Waiting for backup server...
  Attempt 5/30: Waiting for backup server...
  Attempt 6/30: Waiting for backup server...
  Attempt 7/30: Waiting for backup server...
  Attempt 8/30: Waiting for backup server...
  Attempt 9/30: Waiting for backup server...
  Attempt 10/30: Waiting for backup server...
  Attempt 11/30: Waiting for backup server...
  Attempt 12/30: Waiting for backup server...
  Attempt 13/30: Waiting for backup server...
  Attempt 14/30: Waiting for backup server...
  Attempt 15/30: Waiting for backup server...
  Attempt 16/30: Waiting for backup server...
  Attempt 17/30: Waiting for backup server...
  Attempt 18/30: Waiting for backup server...
  Attempt 19/30: Waiting for backup server...
  Attempt 20/30: Waiting for backup server...
  Attempt 21/30: Waiting for backup server...
  Attempt 22/30: Waiting for backup server...
  Attempt 23/30: Waiting for backup server...
  Attempt 24/30: Waiting for backup server...
  Attempt 25/30: Waiting for backup server...
  Attempt 26/30: Waiting for backup server...
  Attempt 27/30: Waiting for backup server...
  Attempt 28/30: Waiting for backup server...
  Attempt 29/30: Waiting for backup server...
  Attempt 30/30: Waiting for backup server...
[ERROR] Backup server failed to start within 30 seconds
The API server may fail to connect to the backup server.
[INFO] Standalone Server GUI launch skipped (embedded GUI is enabled)
       - Use CYBERBACKUP_DISABLE_INTEGRATED_GUI=1 to disable embedded GUI
       - Use CYBERBACKUP_STANDALONE_GUI=1 to force standalone GUI launch
Preparing API Bridge Server (cyberbackup_api_server.py)...

Checking Python dependencies...
c:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\scripts\one_click_build_and_run.py:200: DeprecationWarning: The '__version__' attribute is deprecated and will be removed in Flask 3.2. Use feature detection or 'importlib.metadata.version("flask")' instead.
  version = getattr(imported_module, '__version__', 'unknown version')
[OK] flask (Flask web framework): 3.1.1
[OK] flask_cors (CORS support for Flask API): 6.0.1
[OK] psutil (System process management): 7.0.0
[OK] sentry_sdk (Error monitoring (optional)): unknown version
[OK] cryptography (Cryptographic operations): 45.0.5
[OK] watchdog (File system monitoring): unknown version

[OK] All required Python dependencies are available

Checking port availability...
[OK] Port 9090 is available

Starting API Bridge Server: api_server\cyberbackup_api_server.py
API Bridge Server started with PID: 14588
Waiting for API server to start on 127.0.0.1:9090...
[INFO] Still waiting... (3s/30s)
[INFO] Still waiting... (6s/30s)
[INFO] Still waiting... (9s/30s)
[INFO] Still waiting... (12s/30s)
[INFO] Still waiting... (15s/30s)
[INFO] Still waiting... (18s/30s)
[INFO] Still waiting... (21s/30s)
[INFO] Still waiting... (24s/30s)
[INFO] Still waiting... (27s/30s)
[ERROR] API server failed to start within 30 seconds
[DIAGNOSTIC] Checking system status...
[DEBUG] Port 9090 appears to be available (no process bound)
[ERROR] API Bridge Server failed to start properly


Troubleshooting steps:
1. Check if port 9090 is being used by another application
2. Verify Flask and flask-cors are installed: pip install flask flask-cors
3. Try running manually: python api_server/cyberbackup_api_server.py
4. Check console windows for error messages

[FALLBACK] Manual startup instructions:
Since automatic startup failed, you can try:
1. Open a new terminal/command prompt
2. Navigate to this directory
3. Run: python api_server/cyberbackup_api_server.py
4. Wait for server to start, then open: http://127.0.0.1:9090/

Would you like to try opening the browser anyway? (y/N):