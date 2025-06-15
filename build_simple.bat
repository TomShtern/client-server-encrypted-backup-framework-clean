@echo off
echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

echo Building simple GUI test...

rem Compile simple test
cl.exe /EHsc simple_gui_test.cpp /link user32.lib /out:simple_test.exe

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Running test...
    .\simple_test.exe
) else (
    echo Build failed!
)

if %ERRORLEVEL% EQU 0 (
    echo Build successful!
    echo Running client...
    cd client
    .\EncryptedBackupClient_Simple.exe
) else (
    echo Build failed!
)

pause
