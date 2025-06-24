@echo off
SETLOCAL

REM === Setup Visual Studio Environment ===
SET "VCVARS_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
call "%VCVARS_PATH%"
IF NOT DEFINED VSCMD_VER (
    echo [ERROR] Visual Studio environment not found. Please check VCVARS_PATH.
    exit /b 1
)

echo [BUILD] Compiling RSA test using existing Crypto++ objects...
cl /MD /O2 /EHsc /W3 /DNDEBUG /I"third_party\crypto++" test_rsa_complete.cpp build\cryptopp\*.obj /link /SUBSYSTEM:CONSOLE ws2_32.lib crypt32.lib advapi32.lib /OUT:test_rsa_complete.exe

IF %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] RSA test compiled successfully. Running test...
    echo.
    test_rsa_complete.exe
) ELSE (
    echo [FATAL] RSA test compilation failed!
    exit /b 1
)

ENDLOCAL
