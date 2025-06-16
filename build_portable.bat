@echo off
REM Portable Build Script for Encrypted Backup Framework
REM Automatically detects MSVC installation and builds the project
REM Production-ready build system with comprehensive error handling

setlocal enabledelayedexpansion

echo ================================================================
echo    Encrypted Backup Framework - Production Build System
echo    Portable MSVC Detection and Build
echo ================================================================

REM Initialize build status
set "BUILD_SUCCESS=false"
set "COMPILER_FOUND=false"

REM Function to find MSVC installation
echo [1/8] Detecting MSVC installation...

REM Try to find Visual Studio 2022 first
set "VS_EDITIONS=Professional Enterprise Community BuildTools"
set "VS_YEARS=2022 2019"

for %%Y in (%VS_YEARS%) do (
    for %%E in (%VS_EDITIONS%) do (
        set "VS_PATH=C:\Program Files\Microsoft Visual Studio\%%Y\%%E"
        if exist "!VS_PATH!\VC\Tools\MSVC" (
            echo Found Visual Studio %%Y %%E at: !VS_PATH!
            
            REM Find the latest MSVC version in this installation
            for /f "delims=" %%V in ('dir "!VS_PATH!\VC\Tools\MSVC" /b /ad /on') do (
                set "MSVC_VERSION=%%V"
                set "MSVC_ROOT=!VS_PATH!\VC\Tools\MSVC\!MSVC_VERSION!"
                if exist "!MSVC_ROOT!\bin\Hostx64\x64\cl.exe" (
                    set "CL_PATH=!MSVC_ROOT!\bin\Hostx64\x64\cl.exe"
                    set "LIB_PATH=!MSVC_ROOT!\lib\x64"
                    set "INCLUDE_PATH=!MSVC_ROOT!\include"
                    set "COMPILER_FOUND=true"
                    echo Using MSVC version: !MSVC_VERSION!
                    goto :msvc_found
                )
            )
        )
    )
)

:msvc_found
if "%COMPILER_FOUND%"=="false" (
    echo ERROR: Could not find MSVC compiler installation
    echo Please install Visual Studio 2019 or 2022 with C++ build tools
    echo Available editions: Community, Professional, Enterprise, BuildTools
    pause
    exit /b 1
)

REM Find Windows SDK
echo [2/8] Detecting Windows SDK...
set "SDK_FOUND=false"
set "SDK_VERSIONS=10.0.22621.0 10.0.22000.0 10.0.19041.0 10.0.18362.0"

for %%S in (%SDK_VERSIONS%) do (
    set "SDK_PATH=C:\Program Files (x86)\Windows Kits\10"
    if exist "!SDK_PATH!\lib\%%S\um\x64" (
        set "WIN_SDK_LIB=!SDK_PATH!\lib\%%S\um\x64"
        set "WIN_SDK_UCRT=!SDK_PATH!\lib\%%S\ucrt\x64"
        set "WIN_SDK_INCLUDE=!SDK_PATH!\Include\%%S"
        set "SDK_FOUND=true"
        echo Found Windows SDK version: %%S
        goto :sdk_found
    )
)

:sdk_found
if "%SDK_FOUND%"=="false" (
    echo WARNING: Windows SDK not found, using default paths
    set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
    set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
    set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"
)

REM Set up build environment
echo [3/8] Setting up build environment...
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

REM Create build directories
echo [4/8] Creating build directories...
if not exist "build" mkdir "build"
if not exist "build\client" mkdir "build\client"
if not exist "build\third_party" mkdir "build\third_party"
if not exist "build\third_party\crypto++" mkdir "build\third_party\crypto++"

REM Check for Boost library
echo [5/8] Checking dependencies...
set "BOOST_FOUND=false"
set "BOOST_PATHS=C:\boost C:\lib\boost C:\Users\%USERNAME%\Downloads\boost_1_88_0\boost_1_88_0 C:\dev\boost"

for %%B in (%BOOST_PATHS%) do (
    if exist "%%B\boost" (
        set "BOOST_ROOT=%%B"
        set "BOOST_FOUND=true"
        echo Found Boost library at: %%B
        goto :boost_found
    )
)

:boost_found
if "%BOOST_FOUND%"=="false" (
    echo WARNING: Boost library not found in common locations
    echo Using default path: C:\Users\%USERNAME%\Downloads\boost_1_88_0\boost_1_88_0
    set "BOOST_ROOT=C:\Users\%USERNAME%\Downloads\boost_1_88_0\boost_1_88_0"
)

REM Compile client sources
echo [6/8] Compiling client sources...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"include\client" /I"include\wrappers" /I"third_party\crypto++" /I"%BOOST_ROOT%" /Fo:"build\client\\" ^
src\client\cksum.cpp ^
src\client\client.cpp ^
src\client\main.cpp ^
src\client\protocol.cpp ^
src\client\ClientLogger.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Client source compilation failed
    pause
    exit /b 1
)

REM Compile production wrappers
echo [6/8] Compiling production wrappers...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"include\wrappers" /I"third_party\crypto++" /Fo:"build\client\\" ^
src\wrappers\AESWrapper.cpp src\wrappers\Base64Wrapper.cpp src\wrappers\RSAWrapper.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Wrapper compilation failed
    pause
    exit /b 1
)

REM Compile algebra implementations
echo [6/8] Compiling algebra implementations...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"third_party\crypto++" /Fo:"build\client\\" ^
src\algebra_implementations.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Algebra implementations compilation failed
    pause
    exit /b 1
)

REM Compile Crypto++ sources
echo [7/8] Compiling Crypto++ library...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /DCRYPTOPP_DISABLE_ASM=1 /DCRYPTOPP_DISABLE_X86ASM=1 /DCRYPTOPP_DISABLE_X64ASM=1 /c /I"third_party\crypto++" /Fo:"build\third_party\crypto++\\" ^
third_party\crypto++\base64.cpp ^
third_party\crypto++\cryptlib.cpp ^
third_party\crypto++\files.cpp ^
third_party\crypto++\filters.cpp ^
third_party\crypto++\hex.cpp ^
third_party\crypto++\misc.cpp ^
third_party\crypto++\mqueue.cpp ^
third_party\crypto++\queue.cpp ^
third_party\crypto++\allocate.cpp ^
third_party\crypto++\algparam.cpp ^
third_party\crypto++\basecode.cpp ^
third_party\crypto++\fips140.cpp ^
third_party\crypto++\cpu.cpp ^
third_party\crypto++\rijndael.cpp ^
third_party\crypto++\modes.cpp ^
third_party\crypto++\osrng.cpp ^
third_party\crypto++\sha.cpp ^
third_party\crypto++\iterhash.cpp ^
third_party\crypto++\hrtimer.cpp ^
third_party\crypto++\rdtables.cpp ^
third_party\crypto++\strciphr.cpp ^
third_party\crypto++\rsa.cpp ^
third_party\crypto++\oaep.cpp ^
third_party\crypto++\pubkey.cpp ^
third_party\crypto++\integer.cpp ^
third_party\crypto++\nbtheory.cpp ^
third_party\crypto++\asn.cpp ^
third_party\crypto++\randpool.cpp ^
third_party\crypto++\pkcspad.cpp ^
third_party\crypto++\primetab.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Crypto++ compilation failed
    pause
    exit /b 1
)

REM Clean previous executable
echo [8/8] Linking production executable...
if exist "client\EncryptedBackupClient.exe" (
    echo Removing previous executable...
    del /f "client\EncryptedBackupClient.exe"
    if exist "client\EncryptedBackupClient.exe" (
        echo WARNING: Could not remove previous executable
        echo Please close any running instances and try again
        pause
        exit /b 1
    )
)

REM Link production executable with real RSA
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /Fe:"client\EncryptedBackupClient.exe" ^
build\client\AESWrapper.obj ^
build\client\Base64Wrapper.obj ^
build\client\RSAWrapper.obj ^
build\client\algebra_implementations.obj ^
build\client\cksum.obj ^
build\client\client.obj ^
build\client\main.obj ^
build\client\protocol.obj ^
build\client\ClientLogger.obj ^
build\third_party\crypto++\*.obj ^
ws2_32.lib advapi32.lib user32.lib gdi32.lib shell32.lib crypt32.lib msimg32.lib comdlg32.lib bcrypt.lib /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% neq 0 (
    echo ERROR: Linking failed with error level %ERRORLEVEL%
    echo Common causes:
    echo - Executable is running (close it and try again)
    echo - Missing dependencies
    echo - Library conflicts
    pause
    exit /b 1
)

REM Verify build success
if exist "client\EncryptedBackupClient.exe" (
    echo.
    echo ================================================================
    echo    BUILD SUCCESSFUL - PRODUCTION READY
    echo ================================================================
    echo Executable: client\EncryptedBackupClient.exe
    echo Build type: Production with Real RSA Encryption
    echo Compiler: %CL_PATH%
    echo MSVC Version: %MSVC_VERSION%
    
    REM Get file size for verification
    for %%F in ("client\EncryptedBackupClient.exe") do (
        echo File Size: %%~zF bytes
        echo Last Modified: %%~tF
    )
    
    echo.
    echo The client is ready for production use with:
    echo - Real RSA encryption (Crypto++ library)
    echo - Protocol compatibility with server
    echo - Production-grade error handling
    echo - Optimized build configuration
    echo.
    set "BUILD_SUCCESS=true"
) else (
    echo.
    echo ================================================================
    echo    BUILD FAILED
    echo ================================================================
    echo ERROR: Executable was not created
    echo Please check the compilation errors above
    pause
    exit /b 1
)

echo Build completed successfully!
pause
