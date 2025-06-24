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

echo [BUILD] Compiling entropy verification test...
%CL_PATH% %CFLAGS% entropy_verification.cpp /Fe:EntropyTest.exe crypt32.lib advapi32.lib

IF %ERRORLEVEL% NEQ 0 (echo [FATAL] Test compilation failed! & exit /b 1)

echo [SUCCESS] Test compiled! Running verification...
echo.
EntropyTest.exe

ENDLOCAL
