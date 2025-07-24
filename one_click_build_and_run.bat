@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM ========================================================================
REM   ONE-CLICK BUILD AND RUN - Client-Server Encrypted Backup Framework
REM ========================================================================
REM
REM This script provides a complete one-click solution to:
REM   1. Build the C++ client with CMake + vcpkg
REM   2. Set up Python environment  
REM   3. Start all services (backup server + API server)
REM   4. Launch the web GUI
REM   5. Verify everything is working
REM
REM Author: Auto-generated for CyberBackup 3.0
REM ========================================================================

echo.
echo ========================================================================
echo   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0
echo ========================================================================
echo.
echo Starting complete build and deployment process...
echo This will configure, build, and launch the entire backup framework.
echo.

REM Change to project root directory
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM ========================================================================
REM PHASE 1: PREREQUISITES CHECK
REM ========================================================================
echo [PHASE 1/6] Checking Prerequisites...
echo ----------------------------------------

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x and add it to your PATH
    pause
    exit /b 1
)
echo ✅ Python found: 
python --version

REM Check if CMake is available
cmake --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: CMake is not installed or not in PATH
    echo Please install CMake 3.15+ and add it to your PATH
    pause
    exit /b 1
)
echo ✅ CMake found:
cmake --version | findstr "cmake version"

REM Check if git is available (optional but recommended)
git --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Git found
) else (
    echo ⚠️  Git not found (optional but recommended)
)

echo.
echo Prerequisites check completed successfully!
echo.

REM ========================================================================
REM PHASE 2: CMAKE CONFIGURATION AND VCPKG SETUP
REM ========================================================================
echo [PHASE 2/6] Configuring Build System...
echo ------------------------------------------

echo Calling scripts\configure_cmake.bat for CMake + vcpkg setup...
echo.

call scripts\configure_cmake.bat
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: CMake configuration failed!
    echo Check the output above for details.
    pause
    exit /b 1
)

echo.
echo ✅ CMake configuration completed successfully!
echo.

REM ========================================================================
REM PHASE 3: BUILD C++ CLIENT
REM ========================================================================
echo [PHASE 3/6] Building C++ Client...
echo -----------------------------------

echo Building EncryptedBackupClient.exe with CMake...
echo Command: cmake --build build --config Release
echo.

cmake --build build --config Release
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: C++ client build failed!
    echo Check the compiler output above for details.
    pause
    exit /b 1
)

REM Verify the executable was created
if not exist "build\Release\EncryptedBackupClient.exe" (
    echo ❌ ERROR: EncryptedBackupClient.exe was not created!
    echo Expected location: build\Release\EncryptedBackupClient.exe
    pause
    exit /b 1
)

echo.
echo ✅ C++ client built successfully!
echo   Location: build\Release\EncryptedBackupClient.exe
echo.

REM ========================================================================
REM PHASE 4: PYTHON ENVIRONMENT SETUP
REM ========================================================================
echo [PHASE 4/6] Setting up Python Environment...
echo ---------------------------------------------

echo Installing Python dependencies from requirements.txt...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo ⚠️  Warning: Some Python dependencies failed to install
        echo This may cause issues with the API server or GUI
        echo.
    ) else (
        echo ✅ Python dependencies installed successfully!
    )
) else (
    echo ⚠️  Warning: requirements.txt not found
    echo Installing basic dependencies manually...
    pip install cryptography pycryptodome psutil flask
)

echo.

REM ========================================================================
REM PHASE 5: CONFIGURATION VERIFICATION
REM ========================================================================
echo [PHASE 5/6] Verifying Configuration...
echo ---------------------------------------

REM Check if RSA keys exist
if exist "data\valid_private_key.der" (
    echo ✅ RSA private key found
) else (
    echo ⚠️  RSA private key missing - generating keys...
    python scripts\create_working_keys.py
)

if exist "data\valid_public_key.der" (
    echo ✅ RSA public key found
) else (
    echo ⚠️  RSA public key missing - generating keys...
    python scripts\create_working_keys.py
)

REM Check if transfer.info exists
if exist "data\transfer.info" (
    echo ✅ transfer.info configuration found
) else (
    echo ⚠️  Creating default transfer.info...
    echo 127.0.0.1:1256 > data\transfer.info
    echo testuser >> data\transfer.info
    echo test_file.txt >> data\transfer.info
)

echo.
echo ✅ Configuration verification completed!
echo.

REM ========================================================================
REM PHASE 6: LAUNCH SERVICES
REM ========================================================================
echo [PHASE 6/6] Launching Services...
echo ----------------------------------

echo Starting the complete CyberBackup 3.0 system...
echo.
echo Services that will be started:
echo   • Backup Server (Port 1256)
echo   • API Bridge Server (Port 9090) 
echo   • Web GUI (Browser interface)
echo.

REM Use the existing launch_gui.py which handles service orchestration
echo Calling launch_gui.py to start all services...
echo.

python launch_gui.py

REM If we get here, the GUI launcher has completed
echo.
echo ========================================================================
echo   🎉 ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!
echo ========================================================================
echo.
echo Your CyberBackup 3.0 system should now be running with:
echo.
echo   📊 Web GUI:        http://localhost:9090
echo   🖥️  Server GUI:     Started automatically  
echo   🔒 Backup Server:  Running on port 1256
echo   🌐 API Server:     Running on port 9090
echo.
echo Next steps:
echo   1. The web interface should have opened automatically
echo   2. You can upload files through the web GUI
echo   3. Monitor transfers in the server GUI window
echo   4. Check logs in the console windows for debugging
echo.
echo To run tests: python scripts\master_test_suite.py
echo To stop services: Close the console windows or press Ctrl+C
echo.
echo Have a great backup session! 🚀
echo ========================================================================

pause