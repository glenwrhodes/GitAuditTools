@echo off
REM GitHub Auditing Tool - Windows Batch Script
REM This script runs the GitHub audit tool with the virtual environment activated

cd /d "%~dp0"
.venv\Scripts\python.exe github_audit_tool.py %* 