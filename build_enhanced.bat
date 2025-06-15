@echo off
REM Enhanced build script for fully compliant client
echo Building Enhanced Encrypted Backup Client with full compliance...

set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
set "LIB_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
set "INCLUDE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"

REM Set environment variables for the compiler
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

REM Create build directories
if not exist "build" mkdir "build"
if not exist "build\enhanced" mkdir "build\enhanced"
if not exist "build\third_party" mkdir "build\third_party"
if not exist "build\third_party\crypto++" mkdir "build\third_party\crypto++"

echo Compiling enhanced client sources with full compliance...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++17 /MT /DSTANDALONE_CLIENT /c /I"include" /I"include\client" /I"include\wrappers" /I"third_party\crypto++" /I"C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0" /Fo:"build\enhanced\\" ^
src\client\cksum.cpp ^
src\client\client_enhanced.cpp ^
src\client\protocol.cpp ^
src\client\ClientGUI.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Enhanced client compilation failed
    exit /b 1
)

echo Compiling enhanced crypto wrappers...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++17 /MT /c /I"include\wrappers" /I"third_party\crypto++" /Fo:"build\enhanced\\" ^
src\wrappers\AESWrapper.cpp src\wrappers\Base64Wrapper.cpp src\wrappers\RSAWrapper.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Enhanced wrapper compilation failed
    exit /b 1
)

echo Compiling algebra implementations...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++17 /MT /c /I"third_party\crypto++" /Fo:"build\enhanced\\" ^
src\algebra_implementations.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Algebra implementations compilation failed
    exit /b 1
)

echo Compiling required Crypto++ sources...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++17 /DCRYPTOPP_DISABLE_ASM=1 /DCRYPTOPP_DISABLE_X86ASM=1 /DCRYPTOPP_DISABLE_X64ASM=1 /c /I"third_party\crypto++" /Fo:"build\third_party\crypto++\\" ^
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
    exit /b 1
)

REM Clean previous executable
if exist "client\EncryptedBackupClientEnhanced.exe" (
    echo Removing previous enhanced executable...
    del /f "client\EncryptedBackupClientEnhanced.exe"
)

echo Linking enhanced executable...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++17 /MT /Fe:"client\EncryptedBackupClientEnhanced.exe" ^
build\enhanced\AESWrapper.obj ^
build\enhanced\Base64Wrapper.obj ^
build\enhanced\RSAWrapper.obj ^
build\enhanced\algebra_implementations.obj ^
build\enhanced\cksum.obj ^
build\enhanced\client_enhanced.obj ^
build\enhanced\protocol.obj ^
build\enhanced\ClientGUI.obj ^
build\third_party\crypto++\*.obj ^
ws2_32.lib advapi32.lib user32.lib gdi32.lib shell32.lib crypt32.lib msimg32.lib comdlg32.lib bcrypt.lib /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% neq 0 (
    echo ERROR: Enhanced linking failed with error level %ERRORLEVEL%
    exit /b 1
)

if exist "client\EncryptedBackupClientEnhanced.exe" (
    echo ✅ Enhanced build complete. Executable at client\EncryptedBackupClientEnhanced.exe
    echo 🔒 Features: Full spec compliance, chunked transfer, crypto compliance, 3-retry error handling
) else (
    echo ERROR: Enhanced build failed - executable not created
    exit /b 1
)