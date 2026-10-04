@echo off
REM Runs the complete automated test suite (60+ tests).
setlocal
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python -m pytest tests\ -v
echo.
echo Exit code: %ERRORLEVEL%
endlocal
