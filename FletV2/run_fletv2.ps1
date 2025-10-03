# FletV2 Launcher Script
# Ensures the app uses only the flet_venv packages (not user site-packages)

Write-Host "≡ƒתא Launching FletV2 Encrypted Backup Framework..." -ForegroundColor Cyan
Write-Host "Γ£ו Using flet_venv virtual environment" -ForegroundColor Green
Write-Host ""

# Set environment to prevent loading user site-packages
$env:PYTHONNOUSERSITE = "1"

# Run the Flet app
& "$PSScriptRoot\..\flet_venv\Scripts\python.exe" "$PSScriptRoot\main.py"

Write-Host ""
Write-Host "≡ƒתא FletV2 app closed" -ForegroundColor Yellow
