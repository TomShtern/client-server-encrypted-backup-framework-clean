
# PowerShell Test Script for UTF-8 Solution
# Run this in PowerShell 7 to test emoji display

# Set UTF-8 encoding
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

# Run the Python UTF-8 test
python test_utf8_simple.py