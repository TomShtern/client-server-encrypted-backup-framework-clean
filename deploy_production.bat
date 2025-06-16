@echo off
REM Production Deployment Script for Encrypted Backup Framework
REM Comprehensive setup and deployment automation

setlocal enabledelayedexpansion

echo ================================================================
echo    ENCRYPTED BACKUP FRAMEWORK - PRODUCTION DEPLOYMENT
echo    Automated Setup and Configuration
echo ================================================================

set "DEPLOYMENT_SUCCESS=false"
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo [1/10] Checking system requirements...

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%a in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%a"
echo Found Python version: %PYTHON_VERSION%

echo [2/10] Creating production directory structure...

REM Create production directories
set "PRODUCTION_DIRS=config logs backup temp certificates"
for %%d in (%PRODUCTION_DIRS%) do (
    if not exist "%%d" (
        mkdir "%%d"
        echo Created directory: %%d
    )
)

echo [3/10] Setting up configuration management...

REM Create configuration files
python config_manager.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to create configuration files
    pause
    exit /b 1
)

echo [4/10] Installing Python dependencies...

REM Install server dependencies
pip install pycryptodome psutil matplotlib --quiet
if %ERRORLEVEL% neq 0 (
    echo WARNING: Some Python packages may not have installed properly
    echo Server will run with basic functionality
)

echo [5/10] Building production client...

REM Build the client using portable build script
call build_portable.bat
if %ERRORLEVEL% neq 0 (
    echo ERROR: Client build failed
    pause
    exit /b 1
)

if not exist "client\EncryptedBackupClient.exe" (
    echo ERROR: Client executable was not created
    pause
    exit /b 1
)

echo [6/10] Setting up database...

REM Initialize the database
python -c "
import sqlite3
import os
db_path = 'defensive.db'
if os.path.exists(db_path):
    print('Database already exists')
else:
    print('Creating new database...')
    # Database will be created by server on first run
"

echo [7/10] Configuring security...

REM Generate RSA keys if they don't exist
if not exist "priv.key" (
    echo Generating RSA private key...
    python -c "
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

# Generate RSA key pair
key = RSA.generate(1024)
private_key = key.export_key('DER')
public_key = key.publickey().export_key('DER')

# Save keys
with open('priv.key', 'wb') as f:
    f.write(private_key)
with open('pub.key', 'wb') as f:
    f.write(public_key)

print('RSA keys generated successfully')
" 2>nul || echo WARNING: Could not generate RSA keys automatically
)

echo [8/10] Setting up logging...

REM Configure logging directories
if not exist "logs" mkdir "logs"
if not exist "client\logs" mkdir "client\logs"

echo [9/10] Creating deployment scripts...

REM Create production start scripts
echo @echo off > start_production_server.bat
echo echo Starting Encrypted Backup Server - Production Mode >> start_production_server.bat
echo python server/server.py --environment production >> start_production_server.bat
echo pause >> start_production_server.bat

echo @echo off > start_production_client.bat
echo echo Starting Encrypted Backup Client - Production Mode >> start_production_client.bat
echo cd client >> start_production_client.bat
echo EncryptedBackupClient.exe >> start_production_client.bat
echo pause >> start_production_client.bat

REM Create system status check script
echo @echo off > check_system_status.bat
echo echo Checking Encrypted Backup Framework Status... >> check_system_status.bat
echo python comprehensive_test_suite.py >> check_system_status.bat
echo pause >> check_system_status.bat

echo [10/10] Running final validation...

REM Run comprehensive test suite
echo Running comprehensive tests...
python comprehensive_test_suite.py
set "TEST_RESULT=%ERRORLEVEL%"

echo.
echo ================================================================
echo    DEPLOYMENT COMPLETE
echo ================================================================

if exist "client\EncryptedBackupClient.exe" (
    echo ✅ Client: READY
    set "CLIENT_STATUS=READY"
) else (
    echo ❌ Client: FAILED
    set "CLIENT_STATUS=FAILED"
)

REM Check server
python -c "import server.server; print('✅ Server: READY')" 2>nul || echo ❌ Server: FAILED

if exist "defensive.db" (
    echo ✅ Database: READY
) else (
    echo ⚠️ Database: Will be created on first run
)

if exist "config\default.json" (
    echo ✅ Configuration: READY
) else (
    echo ❌ Configuration: FAILED
)

echo.
echo Production Files Created:
echo - client\EncryptedBackupClient.exe (Production Client)
echo - server\server.py (Production Server)
echo - config\*.json (Configuration Files)
echo - start_production_server.bat (Server Launcher)
echo - start_production_client.bat (Client Launcher)
echo - check_system_status.bat (System Status Checker)
echo - comprehensive_test_suite.py (Test Suite)

echo.
echo Quick Start Guide:
echo 1. Start server: start_production_server.bat
echo 2. Start client: start_production_client.bat
echo 3. Check status: check_system_status.bat

if "%TEST_RESULT%"=="0" (
    echo.
    echo 🎉 DEPLOYMENT SUCCESSFUL - SYSTEM IS PRODUCTION READY!
    echo.
    echo The Encrypted Backup Framework is now fully configured and ready for use.
    echo All components have been tested and validated.
    set "DEPLOYMENT_SUCCESS=true"
) else (
    echo.
    echo ⚠️ DEPLOYMENT COMPLETED WITH WARNINGS
    echo.
    echo The system has been deployed but some tests failed.
    echo Please review the test results and address any issues.
    echo The system may still be functional for basic operations.
)

echo.
echo For support and documentation, see the docs/ directory.
echo.

pause
exit /b 0
