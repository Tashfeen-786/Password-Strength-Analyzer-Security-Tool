# Windows Execution Guide — exact commands

Prerequisites (install once):
- Python 3.10+ from https://www.python.org/downloads/ (tick "Add python to PATH")
- Node.js 18+ LTS from https://nodejs.org/

All commands run from the project root
(e.g. `cd C:\Users\<you>\Downloads\Password-Strength-Analyzer` — after
extracting the ZIP; paths below also work if the folder has another name).

## 1 · Setup (one command)

```bat
scripts\setup_windows.bat
```
Creates `.venv`, installs backend deps (`requirements.txt`), runs
`npm install` + `npm run build` in `frontend\`.

## 2 · Start the application (API + built UI)

```bat
scripts\start_backend.bat
```
Then open **http://localhost:8000** in your browser.

Interactive API docs: **http://localhost:8000/docs**.

## 3 · Optional: Vite dev server (hot reload for frontend development)

Keep the backend running and open a second terminal:

```bat
scripts\start_frontend.bat
```
Serves http://localhost:5173 (proxies `/api` to :8000 automatically).
For normal use you do NOT need this — the backend already serves the UI.

## 4 · Run the full test suite

```bat
scripts\run_tests.bat
```
Expected: `69 passed` (69 automated tests: 49 analyzer + 9 API + 11 security).

## 5 · Generate local evidence helpers

```bat
scripts\generate_evidence.bat
```
Seeds synthetic demo analytics, runs the educational hashing demo, writes a
project-tree snapshot. For UI screenshots either capture manually per
`screenshots\README.md`, or:

```bat
pip install playwright
playwright install chromium
python scripts\generate_screenshots.py
python scripts\generate_terminal_evidence.py
```
(backend must be running for browser captures; synthetic demo passwords only).

## 6 · Useful one-offs

```bat
.venv\Scripts\python scripts\seed_demo_data.py     :: synthetic dashboard data
.venv\Scripts\python scripts\hashing_demo.py       :: PBKDF2 education demo
python -m uvicorn backend.app:app --reload --port 8000   :: dev backend
```

## Troubleshooting

- **`py` not found** → reinstall Python with "Add to PATH" or use `python`
  in `scripts\setup_windows.bat` (the script tries both automatically).
- **Port 8000 busy** → `netstat -ano | findstr :8000`, stop the other app,
  or edit the port in `scripts\start_backend.bat`.
- **npm install fails behind proxy** → configure npm proxy or use offline
  mirror; the backend API works independently of the frontend build.
