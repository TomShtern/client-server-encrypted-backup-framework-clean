# PowerShell UTF-8 Emoji Test Script
# Save this as test_utf8_emojis.ps1 and run in PowerShell 7

# Set UTF-8 encoding for output
$OutputEncoding = [System.Text.UTF8Encoding]::new()

# Set console code page to UTF-8
chcp 65001 > $null

# Test emoji display using different methods
Write-Host "=== PowerShell UTF-8 Emoji Test ==="

# Method 1: Direct emoji characters
Write-Host "Method 1 - Direct emojis: 🎉 ✅ ❌ 🌍 🚀"

# Method 2: Unicode escape sequences
Write-Host "Method 2 - Unicode escapes: $([char]0x1F389) $([char]0x2705) $([char]0x274C) $([char]0x1F30D) $([char]0x1F680)"

# Method 3: Using [System.Text.Encoding]::UTF8
$emojiString = "Method 3 - UTF8 encoded: 🎉✅❌🌍🚀"
Write-Host $emojiString

# Method 4: Testing with Hebrew text + emojis
$hebrewWithEmojis = "Hebrew with emojis: שלום 🌍 שלום ✅"
Write-Host $hebrewWithEmojis

Write-Host "`n=== Test Complete ==="
Write-Host "If you see question marks or boxes above, try:"
Write-Host "1. Using Windows Terminal instead of Command Prompt"
Write-Host "2. Changing your console font to one that supports emojis (like Cascadia Code PL)"