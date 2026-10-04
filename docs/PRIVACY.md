# Privacy & Data-Minimization Design

This project's core security requirement is that **the tool itself never
becomes a credential store**. Every design decision follows from that.

## The rules and how they are implemented

| Rule | Implementation | Verified by |
|---|---|---|
| No plaintext password storage | Analysis runs in memory; the SQLite schema has **no password column** | `test_password_not_in_database`, screenshot 25 |
| No hashes of submitted passwords | Even hashes of arbitrary user passwords create unnecessary offline-guessing risk; we store neither | `test_password_not_in_database` (hash scan) |
| No password logging | Only method/path/status in server logs; request bodies never logged | `test_password_not_in_logs` |
| No passwords in URLs | Password travels only in POST body; query params are ignored → 422 | `test_password_not_accepted_via_url` |
| Not returned in responses | Response contains derived results only | `test_password_not_in_api_response` |
| Not echoed in errors | Validation handler strips pydantic `input` values → `[redacted]` | `test_validation_error_does_not_echo_password` |
| No browser persistence | No `localStorage` / `sessionStorage` writes exist in the frontend | `test_frontend_does_not_persist_password` |
| Real password field | `<input type="password">`, hidden by default, 👁 show/hide toggle | `test_password_input_is_password_type` |
| No external transmission | Zero outbound calls from the backend; breach demo is local hashes | architecture + code |
| Analytics = metadata only | analysis_id, score, classification, password_length, unique_ratio, weakness_count, created_at; findings store generic type/severity/description — never password content or personal context | `test_analytics_rows_are_metadata_only`, `test_context_is_never_reflected` |

## What the database stores (and why no password/hash column exists)

```sql
ANALYSES(analysis_id, score, classification, password_length,
         unique_character_ratio, weakness_count, created_at)
FINDINGS(finding_id, analysis_id, finding_type, severity, description)
```

- **Plaintext** would turn our own database into a credential leak on breach.
- **Encrypted (reversible)** storage has the same practical effect for anyone
  holding the key — and this tool has no need to recover passwords.
- **Even hashes** of arbitrary user-submitted passwords are an unnecessary
  risk here: the analyzer never needs to verify the user later, and
  low-entropy submissions could be recovered by offline guessing against the
  hash. So we store neither the password nor any hash of it.

## The demo breach check (`data/breached_sha1.txt`)

- SHA-1 hashes of **13 invented synthetic strings** only — this file contains
  no real leaked credentials (it was generated locally by the project author).
- The submitted password is hashed locally and compared in memory; nothing is
  sent anywhere. This demonstrates the *concept* safely.
- Production equivalent: k-anonymity services (Pwned-Passwords style) where
  only the first 5 hex chars of a SHA-1 leave the client.

## Optional personal context

The demo context (first name / birth year / organization) is compared in
memory and **never persisted** — the FINDINGS rows store only generic
descriptions such as "Password appears to contain personal information."

## Production hardening notes

HTTPS everywhere, hardened rate limiting, security headers, disabling the
demo analytics write paths entirely if desired (`PSA_ENABLE_ANALYTICS=false`),
and periodic review that no password-like column ever appears
(`backend.models.database.SAFE_COLUMNS` is the audited allow-list).
