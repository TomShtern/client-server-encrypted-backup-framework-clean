@echo off
echo Running Master Test Suite...
echo ============================

echo.
echo 🐍 Running Python Master Test Suite...
echo ----------------------------------------
python master_test_suite.py
set PYTHON_RESULT=%ERRORLEVEL%

echo.
echo.
echo 🔧 Running C++ Master Test Suite...
echo ------------------------------------

REM Check if C++ test suite is built
if not exist "build\master_test_suite.exe" (
    echo C++ test suite not found. Building it first...
    call build_master_tests.bat
    if errorlevel 1 (
        echo Failed to build C++ test suite
        goto :summary
    )
)

build\master_test_suite.exe
set CPP_RESULT=%ERRORLEVEL%

:summary
echo.
echo ========================================
echo MASTER TEST SUITE SUMMARY
echo ========================================

if %PYTHON_RESULT%==0 (
    echo ✅ Python Tests: PASSED
) else (
    echo ❌ Python Tests: FAILED
)

if %CPP_RESULT%==0 (
    echo ✅ C++ Tests: PASSED
) else (
    echo ❌ C++ Tests: FAILED
)

echo.
if %PYTHON_RESULT%==0 if %CPP_RESULT%==0 (
    echo 🎉 ALL TESTS PASSED! 🎉
    set OVERALL_RESULT=0
) else (
    echo ❌ SOME TESTS FAILED
    set OVERALL_RESULT=1
)

echo.
pause
exit /b %OVERALL_RESULT%
