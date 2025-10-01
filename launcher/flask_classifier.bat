@echo off
echo.
echo =========================================
echo   Thai Character Pattern Classifier
echo        (Flask Server)
echo =========================================
echo.

REM Change to the project root directory (parent of launcher)
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

REM Check if the HTML file exists
if not exist "thai_pattern_classifier.html" (
    echo ERROR: thai_pattern_classifier.html not found!
    echo Expected location: %CD%\
    echo Please make sure the file exists in the project root.
    echo.
    pause
    exit /b 1
)

echo Starting Flask server...
echo.

:restart
REM Run the Flask server
set LAUNCHER_TYPE=batch
python launcher\flask_classifier.py

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