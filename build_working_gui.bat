@echo off
echo =============================================
echo Building WORKING GUI Client
echo =============================================

REM Initialize Visual Studio environment
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

echo.
echo [1/2] Compiling working GUI client...
cl /EHsc /std:c++17 /O2 ^
   /Fe:WorkingGUIClient.exe ^
   working_gui_client.cpp ^
   user32.lib gdi32.lib shell32.lib msimg32.lib

if %ERRORLEVEL% neq 0 (
    echo ERROR: Working GUI compilation failed with error level %ERRORLEVEL%
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS: Working GUI Client built successfully!
echo 🚀 Output: WorkingGUIClient.exe
echo.
echo 🎨 Features included:
echo   ✅ Beautiful gradient background
echo   ✅ Real-time progress animation  
echo   ✅ Interactive connection toggle
echo   ✅ Professional typography
echo   ✅ Responsive design
echo   ✅ Modern visual effects
echo.
echo Ready to run! Execute: WorkingGUIClient.exe
echo.
pause
