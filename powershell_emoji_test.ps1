# PowerShell UTF-8 Emoji Test
# This script sets up proper UTF-8 encoding and tests emoji display

# Set UTF-8 encoding for all streams
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Set console code page to UTF-8
chcp 65001 | Out-Null

Write-Host "PowerShell UTF-8 Emoji Test" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

# Test direct emoji output
Write-Host "`nDirect emoji test:" -ForegroundColor Cyan
Write-Host "🎉 Party Popper"
Write-Host "✅ Check Mark"
Write-Host "❌ Cross Mark"
Write-Host "🌍 Earth Globe"
Write-Host "🚀 Rocket"

# Test with Hebrew text
Write-Host "`nHebrew with emojis:" -ForegroundColor Cyan
Write-Host "שלום 🌍 עולם ✅"

# Test Python integration with proper encoding
Write-Host "`nTesting Python UTF-8 solution:" -ForegroundColor Cyan

# Run Python with proper environment
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

python -c "
import sys
import os

# Test UTF-8 output from Python
print('Python UTF-8 Test')
print('==================')

# Test emojis
print('🎉 Party Popper')
print('✅ Check Mark')
print('❌ Cross Mark')
print('🌍 Earth Globe')
print('🚀 Rocket')

# Test Hebrew with emojis
print('שלום 🌍 עולם ✅')

print('')
print('If you see proper emojis above, the UTF-8 solution is working!')
"