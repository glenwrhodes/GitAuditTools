@echo off
echo GitHub Auditing Tool - GUI Launcher
echo ==================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "github_audit_tool.py" (
    echo Error: github_audit_tool.py not found in current directory
    echo Please run this script from the GitHub Auditing Tool directory
    pause
    exit /b 1
)

if not exist "github_audit_gui.py" (
    echo Error: github_audit_gui.py not found in current directory
    pause
    exit /b 1
)

echo Launching GitHub Auditing Tool GUI...
echo.

REM Try to launch the GUI
python launch_gui.py

if errorlevel 1 (
    echo.
    echo Failed to launch GUI using launcher script
    echo Trying direct launch...
    python github_audit_gui.py
)

if errorlevel 1 (
    echo.
    echo Error: Failed to launch the GUI
    echo Please check that all dependencies are installed:
    echo pip install -r requirements.txt
    pause
) 