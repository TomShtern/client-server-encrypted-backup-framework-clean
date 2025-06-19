@echo off
REM Project root build script (no CMake)
set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
set "LIB_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
set "INCLUDE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"

REM Set environment variables for the compiler
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

REM Create build directories if they don't exist
if not exist "build" mkdir "build"
if not exist "build\client" mkdir "build\client"
if not exist "build\third_party" mkdir "build\third_party"
if not exist "build\third_party\crypto++" mkdir "build\third_party\crypto++"

REM 1) Compile client sources to build\client\
echo Compiling client sources...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"include\client" /I"include\wrappers" /I"third_party\crypto++" /I"C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0" /Fo:"build\client\\" ^
src\client\cksum.cpp ^
src\client\client.cpp ^
src\client\ClientGUI.cpp ^
src\client\main.cpp ^
src\client\protocol.cpp

REM 1.5) Compile wrappers separately to control dependencies
echo Compiling production wrappers (using real Crypto++ RSA implementation)...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /D_SILENCE_STDEXT_ARR_ITERS_DEPRECATION_WARNING /c /I"include\wrappers" /I"third_party\crypto++" /Fo:"build\client\\" ^
src\wrappers\AESWrapper.cpp src\wrappers\Base64Wrapper.cpp src\wrappers\RSAWrapper.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Wrapper compilation failed
    exit /b 1
)

REM 1.6) Compile algebra implementations to resolve template linking errors
echo Compiling algebra implementations...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"third_party\crypto++" /Fo:"build\client\\" ^
src\algebra_implementations.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Algebra implementations compilation failed
    exit /b 1
)

REM Now using real RSA implementation instead of stub
REM src\wrappers\RSAWrapper_stub.cpp (REMOVED - using real implementation)

REM 2) Compile required Crypto++ sources to build\third_party\crypto++\
echo Compiling Crypto++ sources...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /DCRYPTOPP_DISABLE_ASM=1 /DCRYPTOPP_DISABLE_X86ASM=1 /DCRYPTOPP_DISABLE_X64ASM=1 /D_SILENCE_STDEXT_ARR_ITERS_DEPRECATION_WARNING /c /I"third_party\crypto++" /Fo:"build\third_party\crypto++\\" ^
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
REM Removed algebra-problematic files:
REM third_party\crypto++\abstract_implementations.cpp - has algebra template issues
REM third_party\crypto++\algebra_instantiations.cpp - has algebra template issues
REM src\algebra_implementations.cpp - has compilation errors
REM src\cryptopp_helpers_clean.cpp - has duplicate definitions
REM src\cfb_stubs.cpp - has duplicate definitions
REM third_party\crypto++\template_instantiations.cpp - has algebra template issues
REM third_party\crypto++\randpool.cpp - has CFB template issues
REM third_party\crypto++\integer.cpp - has algebra template issues
REM third_party\crypto++\template_instantiations.cpp - has algebra template issues

REM 3) Clean previous executable if it exists
if exist "client\EncryptedBackupClient.exe" (
    echo Removing previous executable...
    del /f "client\EncryptedBackupClient.exe"
    if exist "client\EncryptedBackupClient.exe" (
        echo WARNING: Could not remove previous executable. Build may fail.
        echo Please close any running instances of EncryptedBackupClient.exe
        pause
    )
)

REM 4) Link all object files to create the executable
echo Linking production executable with real RSA...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /Fe:"client\EncryptedBackupClient.exe" ^
build\client\AESWrapper.obj ^
build\client\Base64Wrapper.obj ^
build\client\RSAWrapper.obj ^
build\client\algebra_implementations.obj ^
build\client\cksum.obj ^
build\client\client.obj ^
build\client\ClientGUI.obj ^
build\client\main.obj ^
build\client\protocol.obj ^
build\third_party\crypto++\*.obj ^
ws2_32.lib advapi32.lib user32.lib gdi32.lib shell32.lib crypt32.lib msimg32.lib comdlg32.lib bcrypt.lib /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% neq 0 (
    echo ERROR: Linking failed with error level %ERRORLEVEL%
    echo This might be due to the executable being in use.
    echo Please close any running instances and try again.
    pause
    exit /b 1
)

if exist "client\EncryptedBackupClient.exe" (
    echo Build complete. Executable at client\EncryptedBackupClient.exe
) else (
    echo ERROR: Build failed - executable not created
    exit /b 1
)

REM 1.7) Compile Simple Web Server for HTML Client
echo Compiling Simple Web Server...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /c /I"include\client" /Fo:"build\client\\" ^
src\client\SimpleWebServer.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Simple Web Server compilation failed
    exit /b 1
)

REM 5) Build Simple Web Server for HTML Client
echo Building Simple Web Server for HTML Client...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /Fe:"client\SimpleWebServer.exe" /I"include\client" ^
build\client\SimpleWebServer.obj ^
ws2_32.lib advapi32.lib /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% neq 0 (
    echo WARNING: Simple Web Server linking failed - HTML client may not work
) else (
    if exist "client\SimpleWebServer.exe" (
        echo Simple Web Server built successfully at client\SimpleWebServer.exe
    ) else (
        echo WARNING: Simple Web Server build failed
    )
)
