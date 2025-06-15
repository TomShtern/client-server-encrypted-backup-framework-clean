@echo off
echo =============================================
echo Building Final Simple Client with AES-256-CBC
echo =============================================

REM Clean previous build
if exist simple_client_final.exe del simple_client_final.exe
if exist *.obj del *.obj

echo.
echo [1/4] Compiling AES Crypto implementation...
cl /c /EHsc /O2 /I. /I"third_party/crypto++" ^
   /DWIN32 /D_WIN32_WINNT=0x0601 ^
   aes_crypto.cpp
   
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile aes_crypto.cpp
    pause
    exit /b 1
)

echo [2/4] Compiling final simple client...
cl /c /EHsc /O2 /I. /I"third_party/crypto++" ^
   /DWIN32 /D_WIN32_WINNT=0x0601 ^
   simple_client_final.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile simple_client_final.cpp
    pause
    exit /b 1
)

echo [3/4] Checking for required Crypto++ objects...

REM Build essential Crypto++ components if not present
set CRYPTO_NEEDED=0
for %%f in (rsa.obj integer.obj nbtheory.obj algparam.obj asn.obj oaep.obj sha.obj misc.obj osrng.obj randpool.obj aes.obj rijndael.obj modes.obj filters.obj cryptlib.obj base64.obj files.obj) do (
    if not exist "third_party\crypto++\%%f" (
        set CRYPTO_NEEDED=1
        goto build_crypto
    )
)

:build_crypto
if %CRYPTO_NEEDED% equ 1 (
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
    echo ✅ Crypto++ objects built successfully
) else (
    echo ✅ All required Crypto++ objects found
)

echo [4/4] Linking final executable...

cl /Fe:simple_client_final.exe ^
   simple_client_final.obj aes_crypto.obj ^
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

if exist simple_client_final.exe (
    echo.
    echo =============================================
    echo BUILD SUCCESSFUL!
    echo =============================================
    echo.
    echo 🔒 Final Simple Client with AES-256-CBC ready!
    echo.
    echo Features:
    echo   ✅ Protocol Version 3 compliant
    echo   ✅ AES-256-CBC encryption with zero IV
    echo   ✅ PKCS7 padding (server compatible)
    echo   ✅ Little-endian binary protocol
    echo   ✅ Proper file encryption/transfer
    echo.
    echo To run:
    echo   1. Make sure you have transfer.info with server:port, username, file_path
    echo   2. Start the Python server: python server/server.py
    echo   3. Run: simple_client_final.exe
    echo.
    echo The client will encrypt your file with AES-256-CBC and send it to the server.
    echo The server will decrypt it using the exact same parameters.
) else (
    echo ERROR: Executable not created
    pause
    exit /b 1
)

echo.
echo Build artifacts:
if exist simple_client_final.exe echo   - simple_client_final.exe (Final encrypted client)
if exist aes_crypto.obj echo   - aes_crypto.obj (AES crypto object)
if exist simple_client_final.obj echo   - simple_client_final.obj (Client object)

echo.
pause