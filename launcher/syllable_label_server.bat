@echo off
echo ====================================
echo Thai Syllable Labeling System
echo ====================================
echo.
echo Starting Flask server...
echo Server will find an available port between 5001-5010
echo.

cd /d "%~dp0\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python or make sure it's in your PATH
    echo.
    pause
    exit /b 1
)

REM Check if the main Python file exists
if not exist "thai_labeling_app.py" (
    echo ERROR: thai_labeling_app.py not found!
    echo Expected location: %CD%\
    echo Please make sure the file exists in the project root.
    echo.
    pause
    exit /b 1
)

:restart
REM Run the Flask server
set LAUNCHER_TYPE=batch
python thai_labeling_app.py

REM Check the exit code
if %errorlevel% equ 0 (
    echo.
    echo Server shut down normally.
    goto end
) else (
    echo.
    echo Server restarting... (exit code: %errorlevel%)
    echo.
    timeout /t 2 /nobreak >nul
    goto restart
)

:end
echo.
echo Server shut down normally.
pause