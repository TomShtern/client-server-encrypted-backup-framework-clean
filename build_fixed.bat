@echo off
setlocal EnableDelayedExpansion

echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
if %ERRORLEVEL% neq 0 (
    echo Failed to set up Visual Studio environment
    exit /b 1
)

echo Checking for running instances...
tasklist | findstr /i "EncryptedBackupClient.exe" > nul
if %ERRORLEVEL% equ 0 (
    echo WARNING: EncryptedBackupClient.exe is running. Please close it before building.
    taskkill /im EncryptedBackupClient.exe /f
    if %ERRORLEVEL% neq 0 (
        echo WARNING: Could not terminate running instance.
    )
)

echo Removing previous executable...
if exist client\EncryptedBackupClient.exe (
    del /f /q client\EncryptedBackupClient.exe
    if %ERRORLEVEL% neq 0 (
        echo WARNING: Could not remove previous executable. It might be in use.
    )
)

echo Compiling client sources...
cl /EHsc /I include /I include/client /I third_party /D _WIN32 /D _DEBUG /Fe:client\EncryptedBackupClient.exe ^
    src\client\main.cpp ^
    src\client\cksum.cpp ^
    src\client\ClientGUI.cpp ^
    src\client\protocol.cpp ^
    /link user32.lib shell32.lib gdi32.lib /DEBUG /NODEFAULTLIB:libcmt.lib /DEFAULTLIB:msvcrtd.lib
if %ERRORLEVEL% neq 0 (
    echo ERROR: Compilation failed with error level %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Build completed successfully.
echo Executable created at client\EncryptedBackupClient.exe

pause
