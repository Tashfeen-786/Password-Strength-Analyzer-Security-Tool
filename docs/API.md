# API Documentation

Base URL: `http://localhost:8000` · Interactive OpenAPI docs: `http://localhost:8000/docs`

## Privacy contract (all endpoints)

- Passwords arrive **only** in POST request bodies — never in URLs.
- Passwords are **processed transiently in memory**; they are never logged,
  never written to the database, never sent to external services, and never
  returned in responses or error messages.
- Validation errors (422) are **redacted** — pydantic `input` values are
  stripped and replaced with `[redacted]`.
- Demo-grade in-memory rate limiting: 60 requests / 60 s per client → `429`.
- In production, serve behind **HTTPS** (passwords must be protected in
  transit) and use a hardened rate limiter.

## POST /api/analyze

Run the complete analysis pipeline.

**Request**
```json
{
  "password": "ApiDemo-Synthetic-7788!",
  "context": { "first_name": "", "birth_year": "", "organization": "" },
  "policy": { "minimum_length": 12 }
}
```
- `password` (string, required, 0–128 chars) — processed transiently.
- `context` (object, optional) — demo-only personal context, never stored.
- `policy` (object, optional) — overrides: `minimum_length`,
  `common_password_check`, `personal_info_check`, `allow_spaces`.

**Response 200**
```json
{
  "score": 71,
  "classification": "STRONG",
  "findings": [ { "type": "dictionary_word", "severity": "medium",
                  "title": "...", "description": "...", "detail": "..." } ],
  "suggestions": ["...specific, actionable, password-free..."],
  "metrics": {
    "length": { "length": 24, "band": "Strong length contribution", ... },
    "characters": { "lowercase": 12, "uppercase": 2, "digits": 4,
                    "symbols": 6, "spaces": 0, "character_type_count": 4,
                    "unique_character_count": 20,
                    "unique_character_ratio": 0.833 },
    "entropy": { "length": 24, "pool_size": 95, "entropy_bits": 157.8,
                 "formula": "Entropy ~= L x log2(N)", "limitation": "..." },
    "guess_resistance": "about 26,500 centuries (educational estimate only)",
    "passphrase_style_detected": false,
    "score_breakdown": { "contributions": { ... }, "penalties": { ... },
                         "total_penalty": 16, "breach_cap_applied": false }
  },
  "policy": { "policy_result": "POLICY PASS", "passed": true,
              "policy": { ... }, "rules": [ ... ] },
  "breach_check": { "checked": true, "found": false, "corpus_size": 10,
                    "demo": true, "note": "EDUCATIONAL DEMO ONLY ..." },
  "disclaimer": "...project-defined, educational estimates...",
  "meta": { "privacy": "Password was processed in memory only...",
            "analytics_recorded": true }
}
```

**Errors**
| Status | Cause | Body |
|---|---|---|
| 422 | missing/bad body, password > 128 chars, wrong types | redacted details |
| 429 | rate limit exceeded | `{ "detail": "Rate limit exceeded..." }` |

## POST /api/generate-password

```json
{ "mode": "password", "length": 20, "uppercase": true,
  "lowercase": true, "numbers": true, "symbols": true }
```
or `{ "mode": "passphrase", "words": 4, "separator": "-" }`

→ `{ "mode": "password", "generated": "...", "note": "...'secrets'...",
     "privacy": "Nothing about this request is persisted." }`

Validation: `length ∈ [8,64]`, `words ∈ [3,8]`, `mode ∈ {password,passphrase}`.

## GET /api/dashboard/stats

Aggregate statistics (safe metadata only):

```json
{ "total_analyses": 31, "average_score": 42.7,
  "classifications": { "VERY WEAK": 11, "WEAK": 6, "MODERATE": 2,
                       "STRONG": 9, "VERY STRONG": 3 },
  "length_distribution": [ { "length": 5, "n": 3 }, ... ],
  "score_distribution": [ { "band": "0-9", "count": 7 }, ... ],
  "privacy_note": "Aggregate metadata only..." }
```

## GET /api/analytics/weaknesses

```json
{ "weakness_types": [ { "type": "dictionary_word", "severity": "medium",
                        "count": 9 } ],
  "pattern_frequency": [ { "type": "sequential_pattern", "count": 4 } ],
  "note": "Finding types/severities only..." }
```

## GET /api/health

→ `{"status":"ok","service":"password-strength-analyzer"}`
