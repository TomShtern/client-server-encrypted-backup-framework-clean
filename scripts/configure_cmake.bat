@echo off
echo ===============================================
echo  Configuring CMake for Portable Build System
echo ===============================================

cd /d "%~dp0\.."

echo [1/4] Checking vcpkg bootstrap...
if not exist "vcpkg\vcpkg.exe" (
    echo Bootstrapping vcpkg...
    cd vcpkg
    call bootstrap-vcpkg.bat
    cd ..
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: vcpkg bootstrap failed!
        pause
        exit /b 1
    )
)

echo [2/4] Installing dependencies from manifest...
vcpkg\vcpkg.exe install --triplet x64-windows --recurse
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: vcpkg dependency installation failed!
    pause
    exit /b 1
)

echo [3/4] Cleaning previous build cache if it exists...
if exist "build" (
    echo Removing stale build directory...
    rmdir /s /q build
)

echo [4/4] Configuring CMake with vcpkg integration...
cmake -B build -S . ^
    -DCMAKE_TOOLCHAIN_FILE=vcpkg/scripts/buildsystems/vcpkg.cmake ^
    -DVCPKG_TARGET_TRIPLET=x64-windows ^
    -A x64

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =============================================== 
    echo  CMake configuration completed successfully!
    echo ===============================================
    echo.
    echo Next steps:
    echo   1. Build: cmake --build build --config Release
    echo   2. Or open in VS Code and use CMake extension
    echo.
) else (
    echo.
    echo ===============================================
    echo  ERROR: CMake configuration failed! 
    echo ===============================================
    echo Error code: %ERRORLEVEL%
    echo.
    echo Troubleshooting tips:
    echo   1. Check that vcpkg dependencies installed correctly
    echo   2. Verify CMakeLists.txt syntax
    echo   3. Run 'vcpkg integrate install' if needed
    echo.
)
pause
