# Architecture & Folder Guide

## Request flow

```
User → Secure Web Interface (React+Vite)
     → Password Input (type="password", hidden by default)
     → POST /api/analyze (body only)
     → In-Memory Analysis (backend/services/*): length, characters, common
       passwords + dictionary (+ leetspeak), sequences, keyboard walks,
       repetition, predictable structure, year/date, numeric runs, optional
       context, entropy estimation, demo breach check
     → Strength Scoring Engine (0–100) → Classification
     → Suggestion Engine + Policy Checker
     → Response (never contains the password)
     → (optional) safe aggregate metadata → ANALYSES/FINDINGS → Dashboard
```

## Folder structure

```
Password-Strength-Analyzer/
├── backend/                 # FastAPI application
│   ├── app.py               # app factory, middleware (rate limit), redacted
│   │                        # validation errors, static frontend hosting
│   ├── routes/              # HTTP layer only (thin): analyze / dashboard /
│   │                        # generator routers
│   ├── services/            # ALL analysis logic (pure, in-memory, testable)
│   │   ├── password_analyzer.py   # analyze_password() orchestrator
│   │   ├── length_analyzer.py     # length bands + length_score
│   │   ├── character_analyzer.py  # classes, unique counts, ratios
│   │   ├── pattern_detector.py    # sequences, keyboard, repetition,
│   │   │                          # predictable structure, year/date, digits
│   │   ├── common_checker.py      # common passwords, dictionary, leetspeak
│   │   ├── context_checker.py     # optional personal-context overlap
│   │   ├── entropy_estimator.py   # L×log2(N) + limitation + guess label
│   │   ├── scoring_engine.py      # 0–100 score, contributions/penalties
│   │   ├── suggestion_engine.py   # specific, password-free suggestions
│   │   ├── policy_checker.py      # POLICY PASS/FAIL (≠ strength score)
│   │   ├── password_generator.py  # secrets-based generator/passphrase
│   │   ├── breach_checker.py      # local synthetic SHA-1 demo corpus
│   │   ├── analytics_service.py   # metadata-only persistence + aggregates
│   │   └── hashing_demo.py        # standalone educational PBKDF2 demo
│   ├── models/
│   │   ├── database.py        # SQLite schema (NO password column) + DDL dump
│   │   └── schemas.py         # pydantic request models
│   └── utils/
│       ├── config.py          # env-driven settings
│       └── safety.py          # redaction helpers
├── frontend/                # React 18 + Vite 5 (+ Recharts dashboard)
│   └── src/components/      # Analyzer / Generator / Dashboard / Learn pages
├── data/                    # small educational lists + synthetic breach demo
├── tests/                   # 69 tests (analyzer/API/security-privacy)
├── screenshots/             # 28-item evidence checklist + README.md
├── evidence/                # raw captured artifacts (pytest output, schema…)
├── docs/                    # this documentation set
├── reports/                 # project report (markdown)
├── scripts/                 # setup/run/test/evidence scripts (.bat + .sh/.py)
├── requirements.txt
├── .env.example
└── .gitignore
```

## Design choices

- **Services are pure functions** — no I/O inside `services/*` except the
  analytics writer, which receives only derived metrics. That's what makes
  the 69-test suite fast and the privacy properties auditable.
- **Thin routes** — request validation and response shaping only.
- **Two result vocabularies**: transient `findings[].detail` (returned once to
  the requester) vs generic `findings[].description` (persisted; contains no
  password content).
- **Findings tables store generic descriptions**, so even finding rows cannot
  leak password fragments.
- **Same-origin by default** — FastAPI serves the built frontend; the Vite
  dev server proxies `/api` during development.
