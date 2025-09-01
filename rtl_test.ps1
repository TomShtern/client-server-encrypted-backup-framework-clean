# PowerShell RTL Hebrew Test
# Save as rtl_test.ps1

# Set proper encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "POWERShell RTL HEBREW TEST" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Test normal Hebrew
Write-Host "Normal Hebrew: שלום עולם"

# Test with RTL embedding
Write-Host "RTL Embedded: $([char]0x202b)שלום עולם$([char]0x202c)"

# Test mixed text
Write-Host "Mixed: Hello $([char]0x202b)שלום עולם$([char]0x202c) World"

# Test with numbers
Write-Host "With numbers: $([char]0x202b)בדיקה 123$([char]0x202c)"

# Test with emojis
Write-Host "With emojis: $([char]0x202b)שלום 🌍 עולם ✅$([char]0x202c)"