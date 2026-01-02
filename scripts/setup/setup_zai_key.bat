@echo off
REM Z_AI_API_KEY Setup Helper for Windows
REM This batch file helps set up the Z_AI_API_KEY environment variable
REM We must add this to the gitignore file to avoid committing it by mistake as it has secrets.


echo Z_AI_API_KEY Setup Helper
echo ========================
echo.

REM Check if already set
if defined Z_AI_API_KEY (
    echo Current session has Z_AI_API_KEY set.
    set /p overwrite="Do you want to overwrite it? (y/N): "
    if /i not "!overwrite!"=="y" if /i not "!overwrite!"=="Y" (
        echo Setup cancelled.
        goto :end
    )
)

REM Prompt for the key
set /p api_key="Enter your Z_AI_API_KEY: "

if "%api_key%"=="" (
    echo ERROR: No key provided.
    goto :end
)

REM Set for current session
set Z_AI_API_KEY=%api_key%
echo ✓ Set Z_AI_API_KEY for current session

REM Set persistently
setx Z_AI_API_KEY "%api_key%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Set Z_AI_API_KEY persistently (survives reboots)
    echo Note: New command windows will have access to this variable
) else (
    echo ⚠ Failed to set persistently, but session variable is set
)

echo.
echo Setup complete! 🎉
echo.
echo To test: Run 'echo %%Z_AI_API_KEY%%' in command prompt
echo To remove: Use System Properties -^> Environment Variables
echo.
echo Remember: Never log or print API keys in your code!

:end
pause