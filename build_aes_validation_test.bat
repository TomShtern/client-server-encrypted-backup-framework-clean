@echo off
REM Build script for AES validation test

echo Building AES Validation Test...

REM Ensure build directory exists
if not exist "build" mkdir build

REM Set paths for includes and libraries
set INCLUDE_PATH=%CD%
set CRYPTO_PATH=%CD%\third_party\crypto++

REM Compile the test
cl.exe /EHsc /std:c++17 ^
    /I"%INCLUDE_PATH%" ^
    /I"%CRYPTO_PATH%" ^
    test_client_aes_validation.cpp ^
    src\wrappers\AESWrapper.cpp ^
    src\wrappers\Base64Wrapper.cpp ^
    src\cryptopp_helpers.cpp ^
    /link ^
    ws2_32.lib advapi32.lib user32.lib ^
    /OUT:build\test_aes_validation.exe

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build successful! 
    echo Test executable: build\test_aes_validation.exe
    echo.
    echo To run the test:
    echo   build\test_aes_validation.exe
    echo.
) else (
    echo.
    echo ❌ Build failed with error code %errorlevel%
    echo Check the output above for compilation errors.
)

pause