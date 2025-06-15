@echo off
echo Building Comprehensive Test Suite...

REM Set up environment
set VCPKG_ROOT=C:\vcpkg
set BOOST_ROOT=%VCPKG_ROOT%\installed\x64-windows
set CRYPTOPP_ROOT=%VCPKG_ROOT%\installed\x64-windows

REM Create build directory
if not exist "build" mkdir build
cd build

REM Compile test suite
cl /EHsc /std:c++17 /I..\include /I%BOOST_ROOT%\include /I%CRYPTOPP_ROOT%\include ^
   ..\comprehensive_test_suite.cpp ^
   ..\src\wrappers\RSAWrapper.cpp ^
   ..\src\wrappers\AESWrapper.cpp ^
   ..\src\wrappers\Base64Wrapper.cpp ^
   ..\src\client\cksum.cpp ^
   ..\src\client\protocol.cpp ^
   ..\src\client\ClientGUI.cpp ^
   /link ^
   %BOOST_ROOT%\lib\boost_system-vc143-mt-x64-1_84.lib ^
   %CRYPTOPP_ROOT%\lib\cryptopp.lib ^
   bcrypt.lib ^
   ncrypt.lib ^
   crypt32.lib ^
   user32.lib ^
   gdi32.lib ^
   shell32.lib ^
   comctl32.lib ^
   /out:test_suite.exe

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Test suite compiled successfully!
    echo Running tests...
    echo.
    test_suite.exe
) else (
    echo.
    echo ❌ Compilation failed!
    echo Check the error messages above.
)

cd ..
pause
