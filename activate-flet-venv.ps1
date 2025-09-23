#!/usr/bin/env pwsh
# Auto-Activate FletV2 Environment Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Auto-Activating FletV2 Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir

Write-Host "Activating flet_venv environment..." -ForegroundColor Yellow

# Activate the virtual environment
& ".\flet_venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "✓ FletV2 environment is now active!" -ForegroundColor Green
Write-Host "✓ Python interpreter: $env:VIRTUAL_ENV\Scripts\python.exe" -ForegroundColor Green
Write-Host "✓ Ready for development" -ForegroundColor Green
Write-Host ""

# Display environment info
Write-Host "Environment Details:" -ForegroundColor Cyan
Write-Host "  Virtual Environment: $env:VIRTUAL_ENV" -ForegroundColor Gray
Write-Host "  Python Version: $(python --version 2>&1)" -ForegroundColor Gray
Write-Host "  Pip Location: $(where.exe pip)" -ForegroundColor Gray
Write-Host ""

Write-Host "Common Commands:" -ForegroundColor Cyan
Write-Host "  cd FletV2; flet run -r main.py    # Run FletV2 app" -ForegroundColor Gray
Write-Host "  python test_venv_setup.py         # Test environment" -ForegroundColor Gray
Write-Host "  pip list                          # Show packages" -ForegroundColor Gray