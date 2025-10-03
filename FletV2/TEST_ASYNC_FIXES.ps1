# Test Async Fixes - Launch GUI with Real Server
# Run this script to test the async database/analytics fixes

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TESTING ASYNC FIXES FOR DATABASE VIEW" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes on port 8570
Write-Host "[1/3] Cleaning up any existing processes..." -ForegroundColor Yellow
$proc = Get-NetTCPConnection -LocalPort 8570 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
if ($proc) {
    Stop-Process -Id $proc -Force -ErrorAction SilentlyContinue
    Write-Host "   - Killed existing process on port 8570" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "   - Port 8570 is free" -ForegroundColor Green
}

# Launch the GUI
Write-Host ""
Write-Host "[2/3] Launching FletV2 GUI with integrated BackupServer..." -ForegroundColor Yellow
Write-Host "   - Server will run on http://127.0.0.1:8570" -ForegroundColor Gray
Write-Host "   - Database: defensive.db" -ForegroundColor Gray
Write-Host ""

cd $PSScriptRoot
& "..\flet_venv\Scripts\python.exe" "start_with_server.py"

# Note: This script will block while GUI is running
# Press Ctrl+C to stop the server when done testing
