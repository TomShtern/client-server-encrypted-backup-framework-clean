#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch FletV2 GUI with Real BackupServer Integration

.DESCRIPTION
    This PowerShell launcher properly configures the Python environment
    by setting PYTHONNOUSERSITE=1 BEFORE launching Python, preventing
    user site-packages from interfering with the virtual environment.

.EXAMPLE
    .\start_with_server.ps1

.NOTES
    This script must be run from the FletV2 directory.
    The virtual environment must be set up in ../flet_venv/
#>

# Set environment variables BEFORE launching Python
$env:PYTHONNOUSERSITE = "1"
$env:CYBERBACKUP_DISABLE_INTEGRATED_GUI = "1"
$env:CYBERBACKUP_DISABLE_GUI = "1"
# $env:FLET_DASHBOARD_DEBUG = "1"  # Disabled: Causes performance issues with excessive debug logging
# $env:FLET_DASHBOARD_CONTENT_DEBUG = "1"  # Disabled: Causes performance issues

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $RepoRoot "flet_venv\Scripts\python.exe"
$LauncherScript = Join-Path $ScriptDir "start_with_server.py"

# Verify virtual environment exists
if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtual environment not found: $VenvPython" -ForegroundColor Red
    Write-Host "[INFO] Please run 'python -m venv flet_venv' from the repository root" -ForegroundColor Yellow
    exit 1
}

# Verify launcher script exists
if (-not (Test-Path $LauncherScript)) {
    Write-Host "[ERROR] Launcher script not found: $LauncherScript" -ForegroundColor Red
    exit 1
}

# Display configuration
Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "FletV2 GUI Launcher with User Site-Packages Isolation" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "[CONFIG] Environment Variables:" -ForegroundColor Green
Write-Host "  PYTHONNOUSERSITE = $env:PYTHONNOUSERSITE"
Write-Host "  CYBERBACKUP_DISABLE_INTEGRATED_GUI = $env:CYBERBACKUP_DISABLE_INTEGRATED_GUI"
Write-Host "  CYBERBACKUP_DISABLE_GUI = $env:CYBERBACKUP_DISABLE_GUI"
Write-Host ""
Write-Host "[CONFIG] Paths:" -ForegroundColor Green
Write-Host "  Python: $VenvPython"
Write-Host "  Script: $LauncherScript"
Write-Host ""

# Launch Python with -s flag (additional protection against user site-packages)
Write-Host "[LAUNCH] Starting Python with user site-packages disabled..." -ForegroundColor Yellow
Write-Host ""

& $VenvPython -s $LauncherScript

# Capture exit code
$ExitCode = $LASTEXITCODE

if ($ExitCode -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Application exited cleanly" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] Application exited with code $ExitCode" -ForegroundColor Red
}

exit $ExitCode
