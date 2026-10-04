@echo off
REM Optional: Vite dev server with hot reload on port 5173.
REM (For normal use, start_backend.bat alone is enough - FastAPI serves
REM  the built frontend at http://localhost:8000)
setlocal
cd /d "%~dp0\..\frontend"
call npm run dev
endlocal
