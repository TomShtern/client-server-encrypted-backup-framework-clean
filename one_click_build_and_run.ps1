# ========================================================================
#   ONE-CLICK BUILD AND RUN - Client-Server Encrypted Backup Framework
# ========================================================================
#
# This PowerShell script provides a complete one-click solution to:
#   1. Build the C++ client with CMake + vcpkg
#   2. Set up Python environment  
#   3. Start all services (backup server + API server)
#   4. Launch the web GUI
#   5. Verify everything is working
#
# Author: Auto-generated for CyberBackup 3.0
# ========================================================================

param(
    [switch]$SkipBuild,
    [switch]$SkipTests,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Helper function for colored output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

function Write-Phase {
    param([string]$Phase, [string]$Description)
    Write-Host ""
    Write-ColorOutput "[$Phase] $Description" "Magenta"
    Write-ColorOutput ("-" * 50) "DarkGray"
}

# Main script
try {
    Clear-Host
    
    Write-Host ""
    Write-ColorOutput "========================================================================" "Cyan"
    Write-ColorOutput "   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0" "Cyan"
    Write-ColorOutput "========================================================================" "Cyan"
    Write-Host ""
    Write-Info "Starting complete build and deployment process..."
    Write-Info "This will configure, build, and launch the entire backup framework."
    Write-Host ""

    # Change to script directory
    $ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    Set-Location $ScriptPath
    Write-Info "Working directory: $(Get-Location)"

    # ========================================================================
    # PHASE 1: PREREQUISITES CHECK
    # ========================================================================
    Write-Phase "PHASE 1/6" "Checking Prerequisites..."

    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python found: $pythonVersion"
        } else {
            throw "Python not found"
        }
    } catch {
        Write-Error "Python is not installed or not in PATH"
        Write-Info "Please install Python 3.x and add it to your PATH"
        exit 1
    }

    # Check CMake
    try {
        $cmakeVersion = cmake --version 2>&1 | Select-String "cmake version" | Select-Object -First 1
        if ($cmakeVersion) {
            Write-Success "CMake found: $($cmakeVersion.Line)"
        } else {
            throw "CMake not found"
        }
    } catch {
        Write-Error "CMake is not installed or not in PATH"
        Write-Info "Please install CMake 3.15+ and add it to your PATH"
        exit 1
    }

    # Check Git (optional)
    try {
        $gitVersion = git --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Git found"
        }
    } catch {
        Write-Warning "Git not found (optional but recommended)"
    }

    Write-Success "Prerequisites check completed!"

    # ========================================================================
    # PHASE 2: CMAKE CONFIGURATION
    # ========================================================================
    if (-not $SkipBuild) {
        Write-Phase "PHASE 2/6" "Configuring Build System..."

        Write-Info "Calling scripts\configure_cmake.bat for CMake + vcpkg setup..."
        
        $configureProcess = Start-Process -FilePath "scripts\configure_cmake.bat" -Wait -PassThru -NoNewWindow
        if ($configureProcess.ExitCode -ne 0) {
            Write-Error "CMake configuration failed!"
            exit 1
        }

        Write-Success "CMake configuration completed!"
    } else {
        Write-Warning "Skipping build configuration (--SkipBuild specified)"
    }

    # ========================================================================
    # PHASE 3: BUILD C++ CLIENT
    # ========================================================================
    if (-not $SkipBuild) {
        Write-Phase "PHASE 3/6" "Building C++ Client..."

        Write-Info "Building EncryptedBackupClient.exe with CMake..."
        Write-Info "Command: cmake --build build --config Release"

        $buildProcess = Start-Process -FilePath "cmake" -ArgumentList "--build", "build", "--config", "Release" -Wait -PassThru -NoNewWindow
        if ($buildProcess.ExitCode -ne 0) {
            Write-Error "C++ client build failed!"
            exit 1
        }

        # Verify executable exists
        $exePath = "build\Release\EncryptedBackupClient.exe"
        if (Test-Path $exePath) {
            Write-Success "C++ client built successfully!"
            Write-Info "Location: $exePath"
        } else {
            Write-Error "EncryptedBackupClient.exe was not created!"
            Write-Info "Expected location: $exePath"
            exit 1
        }
    } else {
        Write-Warning "Skipping C++ build (--SkipBuild specified)"
    }

    # ========================================================================
    # PHASE 4: PYTHON ENVIRONMENT SETUP
    # ========================================================================
    Write-Phase "PHASE 4/6" "Setting up Python Environment..."

    if (Test-Path "requirements.txt") {
        Write-Info "Installing Python dependencies from requirements.txt..."
        try {
            python -m pip install -r requirements.txt
            Write-Success "Python dependencies installed successfully!"
        } catch {
            Write-Warning "Some Python dependencies failed to install"
            Write-Info "This may cause issues with the API server or GUI"
        }
    } else {
        Write-Warning "requirements.txt not found"
        Write-Info "Installing basic dependencies manually..."
        try {
            python -m pip install cryptography pycryptodome psutil flask
            Write-Success "Basic dependencies installed!"
        } catch {
            Write-Warning "Failed to install basic dependencies"
        }
    }

    # ========================================================================
    # PHASE 5: CONFIGURATION VERIFICATION
    # ========================================================================
    Write-Phase "PHASE 5/6" "Verifying Configuration..."

    # Check RSA keys
    if (Test-Path "data\valid_private_key.der") {
        Write-Success "RSA private key found"
    } else {
        Write-Warning "RSA private key missing - generating keys..."
        python scripts\create_working_keys.py
    }

    if (Test-Path "data\valid_public_key.der") {
        Write-Success "RSA public key found"
    } else {
        Write-Warning "RSA public key missing - may need key generation"
    }

    # Check transfer.info
    if (Test-Path "data\transfer.info") {
        Write-Success "transfer.info configuration found"
    } else {
        Write-Warning "Creating default transfer.info..."
        @"
127.0.0.1:1256
testuser
test_file.txt
"@ | Out-File -FilePath "data\transfer.info" -Encoding ASCII
    }

    Write-Success "Configuration verification completed!"

    # ========================================================================
    # PHASE 6: LAUNCH SERVICES
    # ========================================================================
    Write-Phase "PHASE 6/6" "Launching Services..."

    Write-Info "Starting the complete CyberBackup 3.0 system..."
    Write-Host ""
    Write-Info "Services that will be started:"
    Write-Info "  • Backup Server (Port 1256)"
    Write-Info "  • API Bridge Server (Port 9090)"
    Write-Info "  • Web GUI (Browser interface)"
    Write-Host ""

    Write-Info "Calling launch_gui.py to start all services..."
    python launch_gui.py

    # Success message
    Write-Host ""
    Write-ColorOutput "========================================================================" "Green"
    Write-ColorOutput "   🎉 ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!" "Green"
    Write-ColorOutput "========================================================================" "Green"
    Write-Host ""
    Write-Success "Your CyberBackup 3.0 system should now be running with:"
    Write-Host ""
    Write-Info "  📊 Web GUI:        http://localhost:9090"
    Write-Info "  🖥️  Server GUI:     Started automatically"
    Write-Info "  🔒 Backup Server:  Running on port 1256"
    Write-Info "  🌐 API Server:     Running on port 9090"
    Write-Host ""
    Write-Info "Next steps:"
    Write-Info "  1. The web interface should have opened automatically"
    Write-Info "  2. You can upload files through the web GUI"
    Write-Info "  3. Monitor transfers in the server GUI window"
    Write-Info "  4. Check logs in the console windows for debugging"
    Write-Host ""
    Write-Info "To run tests: python scripts\master_test_suite.py"
    Write-Info "To stop services: Close the console windows or press Ctrl+C"
    Write-Host ""
    Write-Success "Have a great backup session! 🚀"
    Write-ColorOutput "========================================================================" "Green"

} catch {
    Write-Host ""
    Write-Error "An error occurred during the build and launch process:"
    Write-Error $_.Exception.Message
    if ($Verbose) {
        Write-Host "Stack trace:" -ForegroundColor Red
        Write-Host $_.ScriptStackTrace -ForegroundColor Red
    }
    Write-Host ""
    Write-Info "Please check the error message above and try again."
    Write-Info "You can run with -Verbose for more detailed error information."
    exit 1
} finally {
    # Reset error action preference
    $ErrorActionPreference = "Continue"
}

# Keep console open
Read-Host "Press Enter to continue..."