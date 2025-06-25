@echo off
echo Building Encrypted Backup Client with CMake...

REM Initialize Visual Studio environment
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64

REM Configure CMake
cmake -B build -S . -DCMAKE_TOOLCHAIN_FILE=C:/Users/tom7s/vcpkg/scripts/buildsystems/vcpkg.cmake -A x64

REM Build the project
cmake --build build --config Release

REM Check if build was successful
if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
) else (
    echo Build failed with error code %ERRORLEVEL%
)

exit /b %ERRORLEVEL%
