@echo off
echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

echo Building ULTRA MODERN GUI demo...

rem Compile modern GUI demo
cl.exe /EHsc modern_gui_demo.cpp /link user32.lib gdi32.lib shell32.lib msimg32.lib /out:ModernBackupGUI.exe

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Starting the AMAZING new GUI...
    .\ModernBackupGUI.exe
) else (
    echo Build failed!
    pause
)
