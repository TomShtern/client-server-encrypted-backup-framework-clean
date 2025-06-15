@echo off
echo Building Enhanced GUI Client...

REM Set up Visual Studio environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

REM Clean previous build
if exist "client\EncryptedBackupClient.exe" (
    echo Removing previous executable...
    del /f "client\EncryptedBackupClient.exe"
)

REM Compile with enhanced GUI
echo Compiling enhanced GUI client...
cl /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT ^
   /I"include" /I"include/client" /I"include/wrappers" ^
   src/client/client.cpp ^
   src/client/ClientGUI.cpp ^
   src/wrappers/RSAWrapper_stub.cpp ^
   src/wrappers/AESWrapper.cpp ^
   src/wrappers/Base64Wrapper.cpp ^
   /Fe:client/EncryptedBackupClient.exe ^
   /link user32.lib gdi32.lib shell32.lib comctl32.lib msimg32.lib comdlg32.lib ws2_32.lib

if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed with error level %ERRORLEVEL%
    pause
    exit /b 1
)

if exist "client\EncryptedBackupClient.exe" (
    echo Build complete! Enhanced GUI client ready.
    echo Starting the enhanced client...
    cd client
    EncryptedBackupClient.exe
) else (
    echo ERROR: Build failed - executable not created
    pause
    exit /b 1
)
