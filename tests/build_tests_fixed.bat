@echo off
REM Build script for comprehensive test suite using same environment as main build
echo Building Comprehensive Test Suite...

REM Use same compiler paths as main build
set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
set "LIB_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
set "INCLUDE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"

REM Set environment variables for the compiler
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

REM Create build directory
if not exist "build" mkdir build

REM Clean previous test executable
if exist "build\test_suite.exe" del /f "build\test_suite.exe"

REM Compile test suite with same flags as main build
echo Compiling test suite...
"%CL_PATH%" /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT /D_SILENCE_STDEXT_ARR_ITERS_DEPRECATION_WARNING ^
   /I"include\client" /I"include\wrappers" /I"third_party\crypto++" ^
   /Fe:"build\test_suite.exe" ^
   tests\comprehensive_test_suite.cpp ^
   build\client\cksum.obj ^
   build\client\protocol.obj ^
   build\client\AESWrapper.obj ^
   build\client\Base64Wrapper.obj ^
   build\client\RSAWrapper.obj ^
   build\client\algebra_implementations.obj ^
   build\client\ClientGUI.obj ^
   build\third_party\crypto++\*.obj ^
   ws2_32.lib advapi32.lib user32.lib gdi32.lib shell32.lib crypt32.lib msimg32.lib comdlg32.lib bcrypt.lib ^
   /link /SUBSYSTEM:CONSOLE

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Test suite compiled successfully!
    echo Running tests...
    echo.
    build\test_suite.exe
) else (
    echo.
    echo ❌ Compilation failed with error level %ERRORLEVEL%
    echo Check the error messages above.
)

pause
