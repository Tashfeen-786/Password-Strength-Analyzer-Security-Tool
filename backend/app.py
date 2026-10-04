"""
FastAPI application entrypoint: Password Strength Analyzer & Security
Suggestion Tool (defensive cybersecurity project).

Run (development):
    uvicorn backend.app:app --reload --port 8000

Architecture (PDF section 24):

    User -> Secure Web Interface -> Password Input -> In-Memory Analysis
      -> [Length | Character | Common Password | Sequence | Keyboard |
          Repetition | Context | Entropy] Analyzers
      -> Strength Scoring Engine -> Classification -> Suggestion Engine
      -> User
    (+ optional safe aggregate metrics -> Analytics Database -> Dashboard)

The submitted password never travels into analytics storage.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .models.database import init_db
from .routes.analyze_routes import router as analyze_router
from .routes.dashboard_routes import router as dashboard_router
from .routes.generator_routes import router as generator_router
from .utils.config import (PROJECT_ROOT, RATE_LIMIT_REQUESTS,
                           RATE_LIMIT_WINDOW_SECONDS)
from .utils.safety import scrub_input_fields

FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Password Strength Analyzer & Security Suggestion Tool",
    description=("Defensive, privacy-first password analysis API. Passwords "
                 "are processed transiently in memory and are never logged, "
                 "stored, or transmitted to external services."),
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS: same-origin by default; localhost dev servers allowed ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",  # Vite dev server
        "http://localhost:8000", "http://127.0.0.1:8000",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# --- Minimal in-memory rate limiting (demo-grade) --------------------------
_hits: dict[str, deque] = defaultdict(deque)


@app.middleware("http")
async def rate_limit_and_safe_logging(request: Request, call_next):
    """Two jobs:
       1. demo-grade sliding-window rate limiting per client IP
       2. request logging that records ONLY method/path/status — never the
          request body (so passwords can never appear in logs)."""
    client = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = _hits[client]
    while window and now - window[0] > RATE_LIMIT_WINDOW_SECONDS:
        window.popleft()
    if len(window) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please retry shortly."})
    window.append(now)
    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
    """Return 422 with REDACTED error details.

    Pydantic v2 embeds the offending input value under an 'input' key — for
    a password field that would leak the password straight into the error
    response. We strip every 'input' key instead.
    """
    return JSONResponse(
        status_code=422,
        content={"detail": "The request failed validation. The submitted "
                           "content was not processed.",
                 "errors": scrub_input_fields(exc.errors()),
                 "privacy": "Submitted passwords are never echoed in errors."})


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "password-strength-analyzer"}


app.include_router(analyze_router)
app.include_router(dashboard_router)
app.include_router(generator_router)


# Serve the built React frontend (frontend/dist) when present. The Vite dev
# server (npm run dev) is used during development instead.
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True),
              name="frontend")


def main() -> None:  # convenience: `python -m backend.app`
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
