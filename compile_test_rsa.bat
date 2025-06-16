@echo off
REM Compile simple RSA test
set "CL_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe"
set "LIB_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
set "INCLUDE_PATH=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
set "WIN_SDK_LIB=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\um\x64"
set "WIN_SDK_UCRT=C:\Program Files (x86)\Windows Kits\10\lib\10.0.22621.0\ucrt\x64"
set "WIN_SDK_INCLUDE=C:\Program Files (x86)\Windows Kits\10\Include\10.0.22621.0"

REM Set environment variables for the compiler
set "LIB=%LIB_PATH%;%WIN_SDK_LIB%;%WIN_SDK_UCRT%;%LIB%"
set "INCLUDE=%INCLUDE_PATH%;%WIN_SDK_INCLUDE%\um;%WIN_SDK_INCLUDE%\shared;%WIN_SDK_INCLUDE%\ucrt;%INCLUDE%"

echo Compiling RSA test...
"%CL_PATH%" /EHsc /std:c++14 /MT /I"include\wrappers" /I"third_party\crypto++" test_rsa_simple.cpp build\client\RSAWrapper.obj build\client\Base64Wrapper.obj build\client\algebra_implementations.obj build\third_party\crypto++\*.obj ws2_32.lib advapi32.lib /Fe:test_rsa_simple.exe

if %ERRORLEVEL% equ 0 (
    echo Running RSA test...
    .\test_rsa_simple.exe
) else (
    echo Compilation failed
)
