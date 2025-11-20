#!/usr/bin/env pwsh
# Launch script for C++ API Server

$ErrorActionPreference = "Stop"

Write-Host "==================================================================="
Write-Host "  CyberBackup 3.0 - C++ API Server Launcher"
Write-Host "==================================================================="
Write-Host ""

# Check if executable exists
$exePath = "cpp_api_server\build\Release\cpp_api_server.exe"
if (-not (Test-Path $exePath)) {
    Write-Host "[ERROR] Executable not found: $exePath" -ForegroundColor Red
    Write-Host "[INFO] Run build first: cmake --build cpp_api_server/build --config Release"
    exit 1
}

# Check if config exists
$configPath = "cpp_api_server\config\default_config.json"
if (-not (Test-Path $configPath)) {
    Write-Host "[ERROR] Config not found: $configPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Executable: $exePath" -ForegroundColor Green
Write-Host "[INFO] Config: $configPath" -ForegroundColor Green
Write-Host ""

# Launch server
Write-Host "[INFO] Starting server..." -ForegroundColor Cyan
Write-Host ""

& ".\$exePath" $configPath
