@echo off
setlocal EnableDelayedExpansion

echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to set up Visual Studio environment. Please ensure Visual Studio 2022 is installed.
    pause
    exit /b %ERRORLEVEL%
)

echo Changing to Boost directory...
cd /d "C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to change to Boost directory. Please check if the path is correct.
    pause
    exit /b %ERRORLEVEL%
)

echo Running bootstrap.bat...
call bootstrap.bat
if %ERRORLEVEL% neq 0 (
    echo ERROR: Bootstrap process failed.
    pause
    exit /b %ERRORLEVEL%
)

echo Building Boost libraries...
b2 --build-type=complete stage
if %ERRORLEVEL% neq 0 (
    echo ERROR: Boost build failed.
    pause
    exit /b %ERRORLEVEL%
)

echo Boost build completed successfully.
echo Libraries are located in C:\Users\tom7s\Downloads\boost_1_88_0\boost_1_88_0\stage\lib
pause
