@echo off
echo Closing any running client instances...

REM Kill any running EncryptedBackupClient processes
taskkill /F /IM EncryptedBackupClient.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Closed running client instance
) else (
    echo ℹ️  No running client instances found
)

REM Wait a moment for file handles to be released
timeout /t 2 /nobreak >nul

echo.
echo 🔧 Rebuilding client with dialog fixes...
call build.bat

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCCESS: Client rebuilt with fixes!
    echo 🎯 The dialogs should now be closable with the X button.
    echo.
    echo 🚀 Ready to test! Run the client to see the improvements.
) else (
    echo.
    echo ❌ Build failed. Please check the error messages above.
)

echo.
pause
