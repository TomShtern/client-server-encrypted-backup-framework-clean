@echo off
echo Building Master Test Suite (C++)...
echo =====================================

REM Set up MSVC environment
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" 2>nul
if errorlevel 1 (
    call "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" 2>nul
    if errorlevel 1 (
        echo ERROR: Could not find Visual Studio environment
        echo Please ensure Visual Studio is installed
        pause
        exit /b 1
    )
)

REM Create build directory if it doesn't exist
if not exist "build" mkdir build

REM Clean previous build
del /q build\master_test_suite.exe 2>nul

echo Compiling master_test_suite.cpp...

REM Compile with all necessary includes and libraries
cl /EHsc /std:c++17 ^
   /I"include" ^
   /I"third_party" ^
   master_test_suite.cpp ^
   /Fe:build\master_test_suite.exe ^
   /Fo:build\ ^
   /link

if errorlevel 1 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)

echo.
echo ✅ Master Test Suite compiled successfully!
echo Executable: build\master_test_suite.exe
echo.
echo To run tests: build\master_test_suite.exe
pause
