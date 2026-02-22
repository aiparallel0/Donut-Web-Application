@echo off
REM Quick Fix Batch File for DONUT Receipt Parser
REM This script runs the fixed donut_minimal.py

echo ============================================================
echo DONUT Receipt Parser - Quick Fix
echo ============================================================
echo.
echo This script will:
echo 1. Clear Hugging Face cache (if needed)
echo 2. Run the fixed donut_minimal.py
echo.

REM Option to clear cache
set /p CLEAR_CACHE="Clear Hugging Face cache? (y/n): "
if /i "%CLEAR_CACHE%"=="y" (
    echo Clearing cache...
    rmdir /s /q "%USERPROFILE%\.cache\huggingface" 2>nul
    echo Cache cleared.
    echo.
)

echo Running donut_minimal.py...
echo.
python "%~dp0..\donut_minimal.py"

if errorlevel 1 (
    echo.
    echo ============================================================
    echo ERROR: Script failed to run
    echo ============================================================
    echo.
    echo Troubleshooting:
    echo 1. Ensure Python is installed: python --version
    echo 2. Install dependencies: pip install -r requirements.txt
    echo 3. Check the error messages above
    echo.
    pause
    exit /b 1
)

pause
