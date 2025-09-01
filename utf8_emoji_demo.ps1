# UTF-8 Emoji Display Solution for PowerShell 7
# Save as utf8_emoji_demo.ps1 and run in PowerShell 7

# Configure PowerShell for UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Set console code page to UTF-8
chcp 65001 > $null

Write-Host "PowerShell 7 UTF-8 Emoji Display Demo" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Test emojis using different methods
Write-Host "`nMethod 1 - Direct emojis:" -ForegroundColor Cyan
Write-Host "🎉 Party Popper"
Write-Host "✅ Check Mark" 
Write-Host "❌ Cross Mark"
Write-Host "🌍 Earth Globe"
Write-Host "🚀 Rocket"

Write-Host "`nMethod 2 - Hebrew with emojis:" -ForegroundColor Cyan
Write-Host "שלום 🌍 שלום ✅"

Write-Host "`nMethod 3 - Using Unicode escape sequences:" -ForegroundColor Cyan
Write-Host "$([char]0x1F389) Party Popper"
Write-Host "$([char]0x2705) Check Mark"
Write-Host "$([char]0x274C) Cross Mark"
Write-Host "$([char]0x1F30D) Earth Globe"
Write-Host "$([char]0x1F680) Rocket"

Write-Host "`nTo ensure proper emoji display:" -ForegroundColor Yellow
Write-Host "1. Use Windows Terminal (not Command Prompt)"
Write-Host "2. Install a font that supports emojis (like Cascadia Code PL)"
Write-Host "3. In Windows Terminal settings, set font to Cascadia Code PL or similar"
Write-Host "4. Ensure you're running PowerShell 7 (not Windows PowerShell 5.1)"

Write-Host "`nTesting Python UTF-8 solution with emojis:" -ForegroundColor Green
python utf8_solution_demo.py