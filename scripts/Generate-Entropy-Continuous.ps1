# Generate-Entropy-Continuous.ps1
# This script continuously generates entropy while the client is running
# Run this in a separate PowerShell window before starting the client

Write-Host "Starting continuous entropy generation..." -ForegroundColor Green
Write-Host "Keep this window open while running the client!" -ForegroundColor Yellow

$iteration = 1
while ($true) {
    Write-Host "Entropy generation cycle $iteration..." -ForegroundColor Cyan
    
    # Quick entropy generation activities
    Get-Process | Select-Object -First 50 | Out-Null
    Get-Service | Select-Object -First 50 | Out-Null
    
    # Generate random file operations
    $tempPath = [System.IO.Path]::GetTempPath()
    for ($i = 1; $i -le 10; $i++) {
        $randomFile = Join-Path $tempPath "entropy_continuous_$i.tmp"
        $randomData = -join ((1..100) | ForEach-Object {Get-Random -Maximum 256})
        [System.IO.File]::WriteAllText($randomFile, $randomData)
        if (Test-Path $randomFile) { Remove-Item $randomFile -Force -ErrorAction SilentlyContinue }
    }
    
    # Quick system queries
    Get-ChildItem -Path C:\Windows -ErrorAction SilentlyContinue | Select-Object -First 100 | Out-Null
    
    $iteration++
    Start-Sleep -Milliseconds 500  # Wait 500ms between cycles
}
