# Generate-Entropy.ps1
# This script generates system activity to "warm up" the OS entropy pool.
# Run this immediately before running the C++ client to prevent it from hanging.

Write-Host "Starting aggressive entropy generation to prepare for client launch..." -ForegroundColor Yellow

Write-Host " - Step 1/4: Performing disk I/O scan..."
Get-ChildItem -Path C:\Windows\System32 -ErrorAction SilentlyContinue | Select-Object -First 1000 | Out-Null

Write-Host " - Step 2/4: Querying system processes..."
Get-Process | Out-Null
Get-Service | Select-Object -First 100 | Out-Null

Write-Host " - Step 3/4: Performing network activity..."
try {
    Invoke-WebRequest -Uri "https://www.google.com" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
} catch {
    # Ignore network errors - the attempt itself generates entropy
}
try {
    Invoke-WebRequest -Uri "https://www.microsoft.com" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue | Out-Null
} catch {
    # Ignore network errors - the attempt itself generates entropy
}

Write-Host " - Step 4/4: Generating additional entropy..."
# Generate random file operations
$tempPath = [System.IO.Path]::GetTempPath()
for ($i = 1; $i -le 50; $i++) {
    $randomFile = Join-Path $tempPath "entropy_$i.tmp"
    $randomData = -join ((1..1000) | ForEach {Get-Random -Maximum 256})
    [System.IO.File]::WriteAllText($randomFile, $randomData)
    if (Test-Path $randomFile) { Remove-Item $randomFile -Force -ErrorAction SilentlyContinue }
}

Write-Host " - Step 5/5: Final entropy boost..."
# Additional entropy generation activities
Get-WmiObject -Class Win32_Process | Select-Object -First 100 | Out-Null
Get-EventLog -LogName System -Newest 100 -ErrorAction SilentlyContinue | Out-Null
Get-ChildItem -Path C:\Windows -ErrorAction SilentlyContinue | Select-Object -First 500 | Out-Null

Write-Host "Entropy generation complete. The system is ready." -ForegroundColor Green
Write-Host "You can now run the client application immediately."
