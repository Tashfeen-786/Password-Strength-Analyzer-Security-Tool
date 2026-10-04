@echo off
REM Generates local evidence artifacts:
REM   1. Seeds synthetic demo analytics data
REM   2. Runs the hashing demonstration (educational)
REM   3. Regenerates project-structure listing
REM Requires: setup_windows.bat already completed.
setlocal
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat

echo [1/3] Seeding synthetic demo analytics...
python scripts\seed_demo_data.py

echo [2/3] Hashing demonstration (educational)...
python scripts\hashing_demo.py

echo [3/3] Writing project tree snapshot...
python scripts\tree_snapshot.py

echo.
echo Evidence helpers finished.
echo For UI screenshots, keep the backend running and use the manual
REM capture guide in screenshots\README.md (or scripts\generate_screenshots.py
REM if you have Playwright installed:  pip install playwright ^&^& playwright install chromium)
endlocal
