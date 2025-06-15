@echo off
REM Build complete client with crypto support
echo Building Complete Encrypted Backup Client...

set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
set "LIB_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
set "INCLUDE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"

REM Set environment
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

REM Create output directory
if not exist "build" mkdir "build"

REM Clean previous executables
if exist "complete_client.exe" del /f "complete_client.exe"

REM Compile complete client
echo Compiling complete client with crypto support...
"%CL_PATH%" /EHsc /std:c++17 /MT /Fe:"complete_client.exe" complete_client.cpp simple_crypto.cpp ws2_32.lib /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% neq 0 (
    echo ERROR: Complete client compilation failed with error level %ERRORLEVEL%
    pause
    exit /b 1
)

if exist "complete_client.exe" (
    echo ✅ Complete client build successful!
    echo 🔧 Features: Real RSA keys, AES encryption, full protocol compliance
) else (
    echo ERROR: Complete client build failed - executable not created
    exit /b 1
)