@echo off
REM Minimal build that actually works - no crypto dependencies

REM Set up VS environment
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

REM Create directories
if not exist "build" mkdir "build"
if not exist "build\minimal" mkdir "build\minimal"

echo Building minimal client with working GUI...

REM Compile only the essential files for GUI demo
cl.exe /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT ^
    /I"include\client" ^
    /I"include\wrappers" ^
    /c /Fo:"build\minimal\\" ^
    src\client\main.cpp ^
    src\client\ClientGUI.cpp

if %ERRORLEVEL% neq 0 (
    echo Compilation failed!
    pause
    exit /b 1
)

echo Linking...
link.exe /OUT:"EncryptedBackupClient_Minimal.exe" ^
    /SUBSYSTEM:CONSOLE ^
    build\minimal\main.obj ^
    build\minimal\ClientGUI.obj ^
    user32.lib gdi32.lib shell32.lib advapi32.lib msimg32.lib

if %ERRORLEVEL% neq 0 (
    echo Linking failed!
    pause
    exit /b 1
)

echo Build successful! Running...
.\EncryptedBackupClient_Minimal.exe

pause
