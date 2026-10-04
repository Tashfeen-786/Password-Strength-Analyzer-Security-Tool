@echo off
REM Starts the FastAPI backend (serves API + built frontend) on port 8000.
setlocal
cd /d "%~dp0\.."
call .venv\Scripts\activate.bat
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
endlocal
