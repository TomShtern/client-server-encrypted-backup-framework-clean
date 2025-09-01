# PowerShell UTF-8 Emoji Solution
# This script properly configures UTF-8 and displays emojis

# Set UTF-8 encoding for all streams
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Set console code page to UTF-8
chcp 65001 | Out-Null

# Set environment variables for Python
$env:PYTHONIOENCODING = "utf-8"

Write-Host "PowerShell UTF-8 Emoji Solution" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green

Write-Host "`nTesting emoji display:" -ForegroundColor Cyan

# Test emoji display using different methods
Write-Host "Method 1 - Direct emojis:" -ForegroundColor Yellow
Write-Host "🎉 Party Popper"
Write-Host "✅ Check Mark"
Write-Host "❌ Cross Mark"
Write-Host "🌍 Earth Globe"
Write-Host "🚀 Rocket"

Write-Host "`nMethod 2 - Unicode escape sequences:" -ForegroundColor Yellow
Write-Host "$([char]0x1F389) Party Popper"
Write-Host "$([char]0x2705) Check Mark"
Write-Host "$([char]0x274C) Cross Mark"
Write-Host "$([char]0x1F30D) Earth Globe"
Write-Host "$([char]0x1F680) Rocket"

Write-Host "`nMethod 3 - Hebrew with emojis:" -ForegroundColor Yellow
Write-Host "שלום 🌍 עולם ✅"

Write-Host "`nTesting Python integration:" -ForegroundColor Cyan

# Run Python test with proper environment
python -c @"
import sys
import os

print('Python UTF-8 Test')
print('=================')

# Test that encoding is set correctly
print(f'Stdout encoding: {sys.stdout.encoding}')

# Test emojis
emojis = [
    '🎉 Party Popper',
    '✅ Check Mark',
    '❌ Cross Mark',
    '🌍 Earth Globe',
    '🚀 Rocket',
    'שלום 🌍 עולם ✅'
]

for emoji_text in emojis:
    try:
        print(emoji_text)
    except UnicodeEncodeError as e:
        # Fallback with error handling
        safe_text = emoji_text.encode('utf-8', errors='replace').decode('utf-8')
        print(safe_text)
"@

Write-Host "`nIf you see proper emojis above, the solution is working!" -ForegroundColor Green