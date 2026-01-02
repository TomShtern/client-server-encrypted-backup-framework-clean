# Secure Environment Variable Setup for Z_AI_API_KEY
# This script helps you set up the Z_AI_API_KEY environment variable securely
#we must add this to the gitignore file to avoid committing it by mistake ad it has secrets.

param(
    [switch]$Remove,
    [switch]$SessionOnly,
    [switch]$ShowHelp
)

function Show-Help {
    Write-Host "Z_AI_API_KEY Environment Variable Setup" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This script securely sets up your Z_AI_API_KEY environment variable."
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\setup_zai_key.ps1                 # Interactive setup (recommended)"
    Write-Host "  .\setup_zai_key.ps1 -SessionOnly    # Set for current session only"
    Write-Host "  .\setup_zai_key.ps1 -Remove         # Remove the environment variable"
    Write-Host "  .\setup_zai_key.ps1 -ShowHelp       # Show this help"
    Write-Host ""
    Write-Host "SECURITY NOTES:" -ForegroundColor Yellow
    Write-Host "  - Keys are entered as secure strings (masked input)"
    Write-Host "  - SessionOnly mode doesn't persist across reboots"
    Write-Host "  - Persistent mode stores in Windows user environment"
    Write-Host "  - Never commit keys to version control"
    Write-Host ""
}

if ($ShowHelp) {
    Show-Help
    exit 0
}

if ($Remove) {
    Write-Host "Removing Z_AI_API_KEY from environment..." -ForegroundColor Yellow

    # Remove from current session
    if (Test-Path env:Z_AI_API_KEY) {
        Remove-Item env:Z_AI_API_KEY
        Write-Host "✓ Removed from current session" -ForegroundColor Green
    }

    # Remove from persistent environment
    try {
        Remove-ItemProperty -Path "HKCU:\Environment" -Name "Z_AI_API_KEY" -ErrorAction Stop
        Write-Host "✓ Removed from persistent environment" -ForegroundColor Green
        Write-Host "Note: Sign out and back in for changes to take effect in other applications" -ForegroundColor Cyan
    }
    catch {
        Write-Host "ℹ Z_AI_API_KEY was not set persistently" -ForegroundColor Blue
    }

    exit 0
}

Write-Host "Setting up Z_AI_API_KEY environment variable" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host ""

# Check if already set
$currentValue = $env:Z_AI_API_KEY
if ($currentValue) {
    Write-Host "⚠ Current session has Z_AI_API_KEY set" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -notmatch "^[Yy]$") {
        Write-Host "Setup cancelled." -ForegroundColor Blue
        exit 0
    }
}

# Prompt for the API key securely
$secureKey = Read-Host "Enter your Z_AI_API_KEY" -AsSecureString
$plainKey = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
)

if ([string]::IsNullOrWhiteSpace($plainKey)) {
    Write-Host "❌ No key provided. Setup cancelled." -ForegroundColor Red
    exit 1
}

# Validate key format (basic check - should start with expected pattern)
if ($plainKey.Length -lt 10) {
    Write-Host "❌ Key seems too short. Expected at least 10 characters." -ForegroundColor Red
    exit 1
}

# Set in current session
$env:Z_AI_API_KEY = $plainKey
Write-Host "✓ Set Z_AI_API_KEY for current session" -ForegroundColor Green

# Set persistently unless SessionOnly is specified
if (-not $SessionOnly) {
    try {
        setx Z_AI_API_KEY $plainKey | Out-Null
        Write-Host "✓ Set Z_AI_API_KEY persistently (survives reboots)" -ForegroundColor Green
        Write-Host "Note: New PowerShell/cmd windows will have access to this variable" -ForegroundColor Cyan
    }
    catch {
        Write-Host "❌ Failed to set persistently: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "ℹ Key is still set for current session only" -ForegroundColor Yellow
    }
} else {
    Write-Host "ℹ Session-only mode: Key will be lost when PowerShell closes" -ForegroundColor Blue
}

Write-Host ""
Write-Host "Setup complete! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "To test: Run '`$env:Z_AI_API_KEY' in PowerShell" -ForegroundColor Cyan
Write-Host "To remove: .\setup_zai_key.ps1 -Remove" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remember: Never log or print API keys in your code!" -ForegroundColor Yellow