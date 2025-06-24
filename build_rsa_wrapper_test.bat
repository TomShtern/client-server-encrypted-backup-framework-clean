@echo off
SETLOCAL

REM === Setup Visual Studio Environment ===
SET "VCVARS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
call "%VCVARS_PATH%"
IF NOT DEFINED VSCMD_VER (
    echo [ERROR] Visual Studio environment not found. Please check VCVARS_PATH.
    exit /b 1
)

echo [BUILD] Compiling RSA Wrapper test using existing objects...
cl /MD /O2 /EHsc /W3 /DNDEBUG /I"include" /I"third_party\crypto++" test_rsa_wrapper.cpp build\RSAWrapper.obj build\cryptopp\*.obj /link /SUBSYSTEM:CONSOLE ws2_32.lib crypt32.lib advapi32.lib /OUT:test_rsa_wrapper.exe

IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] RSA Wrapper test compiled successfully. Running test...
    echo.
    echo ================================================
    echo           RUNNING RSA WRAPPER TEST
    echo ================================================
    test_rsa_wrapper.exe
    SET TEST_RESULT=%ERRORLEVEL%
    echo ================================================
    IF %TEST_RESULT% EQU 0 (
        echo ✅ RSA WRAPPER TEST PASSED! No hanging detected.
    ) ELSE (
        echo ❌ RSA WRAPPER TEST FAILED!
    )
    echo ================================================
) ELSE (
    echo [FATAL] RSA Wrapper test compilation failed!
    exit /b 1
)

ENDLOCAL
