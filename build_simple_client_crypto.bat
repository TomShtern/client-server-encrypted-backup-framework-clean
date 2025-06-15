@echo off
echo =============================================
echo Building Enhanced Simple Client with AES Crypto
echo =============================================

REM Clean previous build
if exist simple_client_with_crypto.exe del simple_client_with_crypto.exe
if exist *.obj del *.obj

echo.
echo [1/3] Compiling AES Crypto implementation...
cl /c /EHsc /O2 /I. /I"third_party/crypto++" ^
   /DWIN32 /D_WIN32_WINNT=0x0601 ^
   aes_crypto.cpp
   
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile aes_crypto.cpp
    pause
    exit /b 1
)

echo [2/3] Compiling enhanced simple client...
cl /c /EHsc /O2 /I. /I"third_party/crypto++" ^
   /DWIN32 /D_WIN32_WINNT=0x0601 ^
   simple_client_with_crypto.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile simple_client_with_crypto.cpp
    pause
    exit /b 1
)

echo [3/3] Linking enhanced client executable...

REM First, ensure we have the necessary Crypto++ objects
echo Building required Crypto++ objects...
pushd third_party\crypto++

for %%f in (rsa.cpp integer.cpp nbtheory.cpp algparam.cpp asn.cpp oaep.cpp sha.cpp misc.cpp osrng.cpp randpool.cpp aes.cpp rijndael.cpp modes.cpp filters.cpp cryptlib.cpp base64.cpp files.cpp) do (
    if not exist "%%~nf.obj" (
        echo Building %%f...
        cl /c /EHsc /O2 /DWIN32 /D_WIN32_WINNT=0x0601 %%f
        if !ERRORLEVEL! neq 0 (
            echo ERROR: Failed to build %%f
            popd
            pause
            exit /b 1
        )
    )
)

popd

REM Link the executable
cl /Fe:simple_client_with_crypto.exe ^
   simple_client_with_crypto.obj aes_crypto.obj ^
   third_party/crypto++/rsa.obj ^
   third_party/crypto++/integer.obj ^
   third_party/crypto++/nbtheory.obj ^
   third_party/crypto++/algparam.obj ^
   third_party/crypto++/asn.obj ^
   third_party/crypto++/oaep.obj ^
   third_party/crypto++/sha.obj ^
   third_party/crypto++/misc.obj ^
   third_party/crypto++/osrng.obj ^
   third_party/crypto++/randpool.obj ^
   third_party/crypto++/aes.obj ^
   third_party/crypto++/rijndael.obj ^
   third_party/crypto++/modes.obj ^
   third_party/crypto++/filters.obj ^
   third_party/crypto++/cryptlib.obj ^
   third_party/crypto++/base64.obj ^
   third_party/crypto++/files.obj ^
   ws2_32.lib advapi32.lib user32.lib

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to link executable
    pause
    exit /b 1
)

if exist simple_client_with_crypto.exe (
    echo.
    echo =============================================
    echo BUILD SUCCESSFUL!
    echo =============================================
    echo.
    echo Enhanced Simple Client with AES Crypto built successfully!
    echo.
    echo Usage:
    echo   1. Ensure transfer.info file exists with server details
    echo   2. Ensure RSA private key is available for AES key decryption
    echo   3. Run: simple_client_with_crypto.exe
    echo.
    echo Features:
    echo   - Protocol Version 3 compliance
    echo   - Real AES-256-CBC encryption with zero IV
    echo   - RSA key decryption for AES key
    echo   - PKCS7 padding
    echo   - File encryption before transfer
    echo.
) else (
    echo ERROR: Executable not created
    pause
    exit /b 1
)

echo Build artifacts:
if exist simple_client_with_crypto.exe echo   - simple_client_with_crypto.exe (Enhanced client)
if exist aes_crypto.obj echo   - aes_crypto.obj (AES crypto object)
if exist simple_client_with_crypto.obj echo   - simple_client_with_crypto.obj (Client object)

echo.
echo Ready to test with server!
pause