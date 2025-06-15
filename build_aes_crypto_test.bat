@echo off
echo =============================================
echo Building AES Crypto Test Suite
echo =============================================

REM Clean previous build
if exist test_aes_crypto.exe del test_aes_crypto.exe
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

echo [2/3] Compiling test suite...
cl /c /EHsc /O2 /I. /I"third_party/crypto++" ^
   /DWIN32 /D_WIN32_WINNT=0x0601 ^
   test_aes_crypto.cpp

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to compile test_aes_crypto.cpp
    pause
    exit /b 1
)

echo [3/3] Linking test executable...

REM Collect all necessary Crypto++ object files
set CRYPTO_OBJS=
for %%f in (third_party\crypto++\*.cpp) do (
    set filename=%%~nf
    if exist "%%~nf.obj" (
        set CRYPTO_OBJS=!CRYPTO_OBJS! %%~nf.obj
    )
)

REM Link the executable
cl /Fe:test_aes_crypto.exe ^
   test_aes_crypto.obj aes_crypto.obj ^
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
    echo.
    echo Trying to build required Crypto++ objects...
    
    REM Build essential Crypto++ components
    pushd third_party\crypto++
    
    for %%f in (rsa.cpp integer.cpp nbtheory.cpp algparam.cpp asn.cpp oaep.cpp sha.cpp misc.cpp osrng.cpp randpool.cpp aes.cpp rijndael.cpp modes.cpp filters.cpp cryptlib.cpp base64.cpp files.cpp) do (
        echo Building %%f...
        cl /c /EHsc /O2 /DWIN32 /D_WIN32_WINNT=0x0601 %%f
        if !ERRORLEVEL! neq 0 (
            echo ERROR: Failed to build %%f
            popd
            pause
            exit /b 1
        )
    )
    
    popd
    
    echo.
    echo Retrying link with fresh Crypto++ objects...
    cl /Fe:test_aes_crypto.exe ^
       test_aes_crypto.obj aes_crypto.obj ^
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
       
    if !ERRORLEVEL! neq 0 (
        echo ERROR: Link failed even after building Crypto++ objects
        pause
        exit /b 1
    )
)

if exist test_aes_crypto.exe (
    echo.
    echo =============================================
    echo BUILD SUCCESSFUL!
    echo =============================================
    echo.
    echo Running AES Crypto Test Suite...
    echo.
    test_aes_crypto.exe
    echo.
    echo Test complete. Check results above.
) else (
    echo ERROR: Executable not created
    pause
    exit /b 1
)

echo.
echo Build artifacts:
if exist test_aes_crypto.exe echo   - test_aes_crypto.exe (Test executable)
if exist aes_crypto.obj echo   - aes_crypto.obj (AES crypto object)
if exist test_aes_crypto.obj echo   - test_aes_crypto.obj (Test object)

echo.
echo Ready for integration with simple client!
pause