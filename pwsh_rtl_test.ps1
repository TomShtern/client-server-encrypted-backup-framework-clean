# PowerShell 7 Hebrew RTL Test
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "PowerShell 7 Hebrew RTL Test"
Write-Host "==========================="
Write-Host "Normal Hebrew: שלום עולם"
Write-Host "With RTL embedding: ‫שלום עולם‬"
Write-Host "Mixed text: Hello ‫שלום עולם‬ World"
Write-Host "With emojis: ‫שלום 🌍 עולם ✅‬"