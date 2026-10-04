@echo off
REM ============================================================
REM  Password Strength Analyzer - Windows 1-click setup
REM  Creates venv, installs backend deps, installs + builds frontend
REM ============================================================
setlocal
cd /d "%~dp0\.."

echo [1/4] Creating Python virtual environment (.venv)...
py -3 -m venv .venv || python -m venv .venv
if errorlevel 1 (
  echo ERROR: Python 3.10+ is required. Install from https://python.org and retry.
  exit /b 1
)

echo [2/4] Installing backend dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo [3/4] Installing frontend dependencies (requires Node.js 18+)...
cd frontend
call npm install
if errorlevel 1 (
  echo ERROR: Node.js 18+ is required. Install from https://nodejs.org and retry.
  exit /b 1
)

echo [4/4] Building production frontend (frontend\dist)...
call npm run build
cd ..

echo.
echo Setup complete! Next steps:
echo   scripts\start_backend.bat      - starts API + app at http://localhost:8000
echo   scripts\start_frontend.bat     - optional Vite dev server at http://localhost:5173
echo   scripts\run_tests.bat          - runs all 60+ automated tests
endlocal
