@echo off
echo Building Ultra Modern Encrypted Backup Client...
echo.

REM Set up Visual Studio environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

REM Create output directory
if not exist "ultra_modern_client" mkdir ultra_modern_client

echo Compiling ultra modern client with enhanced GUI...

REM Compile with MSVC
cl /EHsc /D_WIN32_WINNT=0x0601 /std:c++14 /MT ^
   /I"include" /I"include/client" /I"include/wrappers" ^
   /DUNICODE /D_UNICODE ^
   src/client/ultra_modern_client.cpp ^
   src/client/ClientGUI.cpp ^
   /Fe:ultra_modern_client/UltraModernClient.exe ^
   /Fo:ultra_modern_client/ ^
   /link user32.lib gdi32.lib shell32.lib comctl32.lib comdlg32.lib msimg32.lib ws2_32.lib

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ SUCCESS: Ultra Modern Client built successfully!
    echo 📁 Output: ultra_modern_client/UltraModernClient.exe
    echo.
    echo 🚀 Features included:
    echo   • Ultra modern responsive GUI with glass effects
    echo   • Dynamic window scaling and scrollbars
    echo   • Loading animations and toast notifications
    echo   • Multi-column button layout with modern styling
    echo   • Professional color schemes and typography
    echo   • Fully functional button integration
    echo   • Real-time connection status monitoring
    echo   • Advanced progress tracking with animations
    echo.
    echo Ready to run! Execute: ultra_modern_client\UltraModernClient.exe
) else (
    echo.
    echo ❌ ERROR: Ultra Modern Client compilation failed with error level %ERRORLEVEL%
    echo Check the error messages above for details.
)

echo.
pause
