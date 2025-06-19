@echo off
echo Starting Encrypted Backup Client with Entropy Generation...
echo.

echo Step 1: Starting continuous entropy generation in background...
start "Entropy Generator" powershell -ExecutionPolicy Bypass -File Generate-Entropy-Continuous.ps1

echo Step 2: Waiting 3 seconds for entropy to build up...
timeout /t 3 /nobreak > nul

echo Step 3: Starting client...
.\client\EncryptedBackupClient.exe

echo.
echo Client finished. You can close the entropy generation window.
pause
