@echo off
SETLOCAL

REM === Configuration: Point this to your Visual Studio vcvars64.bat ===
SET "VCVARS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
call "%VCVARS_PATH%"
IF NOT DEFINED VSCMD_VER (
    echo [ERROR] Visual Studio environment not found. Please check VCVARS_PATH.
    exit /b 1
)

SET "CL_PATH=cl.exe"
SET "LINK_PATH=link.exe"

REM --- Compiler Flags: /MD is critical for consistency with the C++ standard library DLLs ---
SET "CFLAGS=/MD /O2 /EHsc /W3 /DNDEBUG"

REM --- Linker Flags: Include necessary Windows libraries ---
SET "LINKFLAGS=/SUBSYSTEM:CONSOLE ws2_32.lib crypt32.lib advapi32.lib user32.lib gdi32.lib shell32.lib msimg32.lib comdlg32.lib"

REM === Project Paths ===
SET "CRYPTO_SRC_DIR=third_party\crypto++"
SET "CLIENT_SRC_DIR=src\client"
SET "WRAPPER_SRC_DIR=src\wrappers"
SET "INCLUDE_DIR=include"
SET "BUILD_DIR=build"

REM === Build Process ===
echo [BUILD] Cleaning previous build artifacts...
if exist %BUILD_DIR% rd /s /q %BUILD_DIR%
mkdir %BUILD_DIR%
mkdir %BUILD_DIR%\cryptopp

echo [BUILD] Compiling the authoritative set of Crypto++ sources...
%CL_PATH% %CFLAGS% /c /I"%CRYPTO_SRC_DIR%" /Fo"%BUILD_DIR%\cryptopp\\" ^
    "%CRYPTO_SRC_DIR%\cryptlib.cpp" "%CRYPTO_SRC_DIR%\cpu.cpp" "%CRYPTO_SRC_DIR%\integer.cpp" ^
    "%CRYPTO_SRC_DIR%\misc.cpp" "%CRYPTO_SRC_DIR%\filters.cpp" "%CRYPTO_SRC_DIR%\fips140.cpp" ^
    "%CRYPTO_SRC_DIR%\default.cpp" "%CRYPTO_SRC_DIR%\algparam.cpp" "%CRYPTO_SRC_DIR%\allocate.cpp" ^
    "%CRYPTO_SRC_DIR%\stdcpp.cpp" "%CRYPTO_SRC_DIR%\osrng.cpp" "%CRYPTO_SRC_DIR%\randpool.cpp" ^
    "%CRYPTO_SRC_DIR%\rsa.cpp" "%CRYPTO_SRC_DIR%\nbtheory.cpp" "%CRYPTO_SRC_DIR%\pubkey.cpp" ^
    "%CRYPTO_SRC_DIR%\oaep.cpp" "%CRYPTO_SRC_DIR%\pkcspad.cpp" "%CRYPTO_SRC_DIR%\asn.cpp" ^
    "%CRYPTO_SRC_DIR%\rijndael.cpp" "%CRYPTO_SRC_DIR%\aes.cpp" "%CRYPTO_SRC_DIR%\modes.cpp" ^
    "%CRYPTO_SRC_DIR%\sha.cpp" "%CRYPTO_SRC_DIR%\sha256.cpp" "%CRYPTO_SRC_DIR%\iterhash.cpp" ^
    "%CRYPTO_SRC_DIR%\base64.cpp" "%CRYPTO_SRC_DIR%\hex.cpp" "%CRYPTO_SRC_DIR%\files.cpp"
IF %ERRORLEVEL% NEQ 0 (echo [FATAL] Crypto++ compilation failed! & exit /b 1)

echo [BUILD] Compiling application and wrapper sources...
%CL_PATH% %CFLAGS% /c /I"%INCLUDE_DIR%" /I"%CRYPTO_SRC_DIR%" /Fo"%BUILD_DIR%\\" ^
    "%CLIENT_SRC_DIR%\main.cpp" "%CLIENT_SRC_DIR%\client.cpp" "%CLIENT_SRC_DIR%\protocol.cpp" ^
    "%CLIENT_SRC_DIR%\cksum.cpp" "%WRAPPER_SRC_DIR%\RSAWrapper.cpp" ^
    "%WRAPPER_SRC_DIR%\AESWrapper.cpp" "%WRAPPER_SRC_DIR%\Base64Wrapper.cpp"
IF %ERRORLEVEL% NEQ 0 (echo [FATAL] Application compilation failed! & exit /b 1)

echo [BUILD] Linking executable...
%LINK_PATH% /OUT:"client\EncryptedBackupClient.exe" %LINKFLAGS% ^
    "%BUILD_DIR%\*.obj" ^
    "%BUILD_DIR%\cryptopp\*.obj"
IF %ERRORLEVEL% NEQ 0 (echo [FATAL] Linking failed! & exit /b 1)

echo [SUCCESS] Build completed successfully. Executable is at client\EncryptedBackupClient.exe

ENDLOCAL
