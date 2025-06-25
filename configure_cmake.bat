@echo off
echo Configuring CMake for VS Code...
cd /d "%~dp0"
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=C:/Users/tom7s/vcpkg/scripts/buildsystems/vcpkg.cmake -A x64
if %ERRORLEVEL% EQU 0 (
    echo CMake configuration successful!
) else (
    echo CMake configuration failed with error %ERRORLEVEL%
)
pause
