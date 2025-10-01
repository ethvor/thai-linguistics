@echo off
REM Thai Grapheme Highlighter - Windows Launcher
REM Activates virtual environment and starts Flask server

echo ===============================================
echo Thai Grapheme Highlighting Tool
echo ===============================================
echo.

REM Change to project root directory
cd /d "%~dp0.."

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found at .venv\Scripts\
    echo Attempting to run with system Python...
    echo.
)

REM Start Flask server with restart loop
echo Starting Flask server...
echo.

:restart
python launcher\flask_highlighter.py

REM Check the exit code
if %errorlevel% equ 0 (
    echo.
    echo Server shut down normally.
    goto end
) else (
    echo.
    echo Server restarting... (exit code: %errorlevel%)
    echo.
    timeout /t 1 /nobreak >nul
    goto restart
)

:end
echo.
pause
