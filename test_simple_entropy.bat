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
SET "CFLAGS=/MD /O2 /EHsc /W3 /DNDEBUG"

echo [BUILD] Compiling simple entropy test...
%CL_PATH% %CFLAGS% /I"third_party\crypto++" simple_rsa_test.cpp ^
    build\cryptopp\osrng.obj build\cryptopp\cryptlib.obj build\cryptopp\cpu.obj ^
    build\cryptopp\misc.obj build\cryptopp\randpool.obj build\cryptopp\filters.obj ^
    build\cryptopp\allocate.obj build\cryptopp\algparam.obj build\cryptopp\fips140.obj ^
    build\cryptopp\default.obj /Fe:SimpleRSATest.exe ws2_32.lib crypt32.lib advapi32.lib

IF %ERRORLEVEL% NEQ 0 (echo [FATAL] Simple test compilation failed! & exit /b 1)

echo [SUCCESS] Test compiled! Running entropy test...
echo.
SimpleRSATest.exe

ENDLOCAL
