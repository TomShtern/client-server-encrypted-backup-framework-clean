@echo off
echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" >nul 2>&1

echo Building direct test client...

rem Compile direct test client
cl.exe /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT ^
   /I"include\client" /I"include\wrappers" ^
   test_direct_client.cpp ^
   src\client\client.cpp ^
   src\client\protocol.cpp ^
   src\client\cksum.cpp ^
   src\wrappers\RSAWrapper_stub.cpp ^
   src\wrappers\AESWrapper.cpp ^
   src\wrappers\Base64Wrapper.cpp ^
   /Fe:test_direct_client.exe ^
   /link ws2_32.lib advapi32.lib user32.lib gdi32.lib shell32.lib crypt32.lib msimg32.lib comdlg32.lib bcrypt.lib

if %ERRORLEVEL% neq 0 (
    echo ERROR: Build failed with error level %ERRORLEVEL%
    pause
    exit /b 1
)

echo Build successful!
echo Running direct test...
cd client
..\test_direct_client.exe
pause
