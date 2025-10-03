# PowerShell launcher for FletV2 with real BackupServer integration
# This sets PYTHONNOUSERSITE before Python starts to prevent package conflicts

Write-Host "Setting environment for Flet GUI with server integration..." -ForegroundColor Cyan

# CRITICAL: Set PYTHONNOUSERSITE BEFORE launching Python
$env:PYTHONNOUSERSITE = "1"

# Other environment variables
$env:CYBERBACKUP_DISABLE_INTEGRATED_GUI = "1"
$env:CYBERBACKUP_DISABLE_GUI = "1"
$env:FLET_DASHBOARD_DEBUG = "1"
$env:FLET_DASHBOARD_CONTENT_DEBUG = "1"

Write-Host "Environment configured. Launching FletV2..." -ForegroundColor Green

# Launch Python with the script
& "..\flet_venv\Scripts\python.exe" "start_with_server.py"

# Capture exit code
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Host "Process exited with code: $exitCode" -ForegroundColor Red
}
exit $exitCode
