# Project Report
## Password Strength Analyzer & Security Suggestion Tool

*A defensive, privacy-first cybersecurity course project.*

---

## Abstract

Weak and reused passwords remain a leading cause of account compromise. This
project implements an end-to-end **Password Strength Analyzer & Security
Suggestion Tool**: a React + FastAPI web application that evaluates password
strength in real time across eleven analysis dimensions — length, character
diversity, unique-character ratio, dictionary and common-password occurrence,
sequences, keyboard patterns, repetition, predictable word/number/year
structures, leetspeak variants, optional personal-context overlap, and
entropy-style estimation — and combines them into a transparent,
explainable 0–100 score with a five-band classification. A suggestion engine
converts findings into specific, actionable guidance; a `secrets`-based
generator and a policy checker provide defensive utilities; and a privacy-safe
analytics dashboard aggregates demo statistics — while the architecture
guarantees that submitted passwords are processed transiently in memory and
are never stored, logged, placed in URLs, or transmitted to external
services. Correctness and privacy are verified by 69 automated tests,
including 11 dedicated security tests.

## 1. Introduction

Passwords remain the dominant authentication factor for web applications, and
user-chosen passwords are systematically weaker than their owners believe.
Composition rules ("at least 8 characters, one uppercase, one digit, one
symbol") create a false sense of security: `Password123!` satisfies them all
yet is among the first shapes an attacker tries. This project builds an
educational, industry-oriented tool that evaluates passwords the way modern
security products do — emphasizing **length, unpredictability, pattern
resistance, common-password checks and context** — and coaches users toward
safer choices, all under strict privacy constraints.

## 2. Problem Statement

Users overestimate password strength because existing feedback is shallow.
Three concrete gaps motivate this work:

1. **Composition-only checkers** accept predictable passwords and reject
   nothing that "looks diverse".
2. **Opaque scores** give a color without explaining *why*, so users can't
   learn and fix.
3. **Privacy risks**: naive analyzer tools themselves may log, store, or leak
   the very passwords they evaluate.

The system must therefore (a) analyze multi-dimensionally, (b) explain
transparently, (c) suggest specifically, and (d) guarantee privacy by design.

## 3. Objectives

1. Real-time 0–100 strength scoring and 5-band classification.
2. Detect: dictionary/common passwords, sequences, keyboard patterns,
   repetition, predictable structures, year/date patterns, personal-info
   overlap, leetspeak variants; estimation of theoretical entropy.
3. Generate specific, password-free security suggestions and passphrase
   education.
4. Provide a cryptographically secure demo password generator (`secrets`).
5. Evaluate configurable password policies, kept conceptually separate from
   strength.
6. Demonstrate privacy-safe aggregate analytics (no passwords, no hashes).
7. Verify all of it with automated functional and security tests and produce
   honest evidence.

## 4. Password Security Background

*Authentication* proves identity; *authorization* grants rights. Passwords are
the most common authentication secret. Because servers inevitably get
breached, production systems never store plaintext passwords: they store a
salted, iterated **password hash** (Argon2id, bcrypt, scrypt, PBKDF2), so
verification re-computes rather than decrypts. General-purpose fast hashes
(MD5/SHA-1/SHA-256 alone) are unsuitable because speed benefits offline
guessing. Defense in depth adds **MFA**, rate limiting, lockout/abuse
protection, session security, phishing defense and monitoring. Credential
stuffing — replaying breached password lists against other sites — is why
password **reuse** is as dangerous as password weakness.

## 5. Authentication Security

Password strength is one layer. Real-world login security combines Password +
MFA + Rate Limiting + Secure Password Hashing + Account Lockout / Abuse
Protection + Session Security + Phishing Protection + Monitoring. A very
strong password alone cannot solve phishing or breach-cascade risks; the
tool's suggestions and education module therefore always couple strength
advice with MFA, password-manager and uniqueness guidance.

## 6. Existing Approaches

- **Composition rules** — simple, but accept predictable passwords.
- **zxcvbn-style estimators** — dictionary/pattern graphs with spatial
  analysis; mature and impressive, but heavyweight for teaching.
- **Breach-corpus checks** — k-anonymity APIs (Pwned Passwords) flag known
  leaked passwords without exposing the query.
- **NIST SP 800-63B / OWASP ASVS guidance** — length over forced composition,
  block known-common passwords, no arbitrary rotation.

The proposed system is deliberately **transparent and self-contained**: a
small, readable, fully local engine whose every point and penalty is visible.

## 7. Proposed System

User → Secure Web Interface → Password Input → In-Memory Analysis (length,
character, common-password, dictionary/leetspeak, sequence, keyboard,
repetition, predictable-structure, context, entropy engines) → Strength
Scoring Engine → Classification → Suggestion Engine (+ Policy Checker) →
User. Optional safe aggregate metrics flow to a metadata-only SQLite database
powering the dashboard. **The password itself never enters analytics
storage.**

## 8. Architecture

```
React+Vite SPA ──POST body only──▶ FastAPI (validation, redacted errors,
                                      rate limiting)
                 /api/analyze ──▶ backend/services/* engines (pure functions)
                              └──▶ scoring_engine ──▶ classification
                              └──▶ suggestion_engine + policy_checker
                 /api/generate-password ──▶ secrets-based generator
                 /api/dashboard/stats, /api/analytics/weaknesses ──▶ SQLite
                              (ANALYSES/FINDINGS — no password column)
```

FastAPI serves the built frontend statically (same-origin). Module map and
privacy flow: `docs/ARCHITECTURE.md`, `docs/PRIVACY.md`.

## 9. Password Analysis — Feature Extraction

For each submission the engines derive **metrics only**: length, per-class
counts, `character_type_count`, `unique_character_count` and ratio,
length-band membership, theoretical entropy (`L × log₂ N`), pool size, and a
clearly-labelled educational guess-resistance estimate. Feature extraction is
deterministic and side-effect free.

## 10. Pattern Detection

- **Sequences**: ascending/descending alnum runs ≥ 3 (`123`, `abcd`, `dcba`).
- **Keyboard**: QWERTY row runs (forward ≥ 3, reversed ≥ 4) + curated walks
  (`1qaz2wsx`) — thresholds tuned against English false positives.
- **Repetition**: character runs (`aaaa`) and repeated substrings ≤ 12
  (`abcabcabc`).
- **Structures**: `word + [digits/symbols]` and `word + year` regex frames.
- **Years/dates**: `19xx/20xx` and YMD-like patterns; long digit runs.

## 11. Common Password Detection

A small local educational list (`data/common_passwords.txt`) is matched
case-insensitively, plus a dictionary substring scan and a **leetspeak
normalization** pass (`@→a, 0→o, 3→e, …`) so `P@ssw0rd` reduces to `password`
and is correctly hard-capped at VERY WEAK. Matches display the PDF-required
message: *"Your password matches a commonly used password pattern and should
not be used."*

## 12. Entropy Concepts

`Entropy ≈ L × log₂(N)` estimates the theoretical search space **assuming
random selection** — the report and UI both stress this limitation. Human
passwords aren't random, so `Password123!` scores an optimistic ~79 bits
while remaining predictable; the engine therefore combines entropy with
pattern analysis, and guess-resistance outputs carry the label *"educational
estimate only"* (real resistance depends on attacker model, hashing,
work factor, rate limiting, and online-vs-offline scenarios).

## 13. Strength Scoring

Score = contributions (length ≤35, diversity ≤15, unique ratio ≤10, pattern
resistance ≤20, non-common ≤10, unpredictability ≤10) − penalties (common −40
with cap ≤15, repetition ≤25, personal info ≤30, dictionary ≤12,
structure/sequence/keyboard ≤8 each, year/numeric-run ≤6/4, leetspeak ≤6;
total capped −45), bounded to 0–100. Bands: 0–20 VERY WEAK, 21–40 WEAK,
41–60 MODERATE, 61–80 STRONG, 81–100 VERY STRONG (**project-defined**).
Teaching caps: length <4 ⇒ ≤15; <8 ⇒ ≤25; single character class ⇒ cap by
length; demo breach ⇒ ≤10.

## 14. Recommendation Engine

Findings map to specific, deduplicated suggestions (e.g. *"Your password
contains a predictable sequence of characters — remove runs like ascending
or descending letters/numbers."*) plus standing hygiene guidance (unique
passwords, password manager, MFA). Suggestions never contain the password —
enforced by test.

## 15. Password Generator

Python `secrets` (CSPRNG), never `random`; lengths 16/20/24, per-class
toggles with each enabled class guaranteed present, secure shuffle, plus a
3–8 word passphrase mode. Output is returned once and never stored; the UI
explicitly discourages reuse of demo output and recommends password managers.

## 16. Policy Checker

Configurable policy (min length 12 default, max 128, reject common, reject
personal info, spaces allowed) evaluated as **POLICY PASS/FAIL**, displayed
separately from the strength score. Demonstrated contrast: `aaaaaaaaaaaaaaaa`
passes the length policy yet rates WEAK; `Password123!` passes default policy
yet rates WEAK — showing compliance ≠ strength. Aligned with modern guidance:
length-first, block common/breached, no arbitrary periodic rotation.

## 17. Secure Password Storage Concepts

A standalone educational module (`backend/services/hashing_demo.py`,
`scripts/hashing_demo.py`) demonstrates `password → salt → PBKDF2-HMAC-SHA256
(600k iterations) → stored hash` with `hash_password()`/`verify_password()`:
salt uniqueness (same input, different stored forms), one-way verification,
and hashing-vs-encryption distinctions. It is deliberately **not** integrated
with the analyzer — analyzer input is never persisted anywhere.

## 18. Privacy Design

See `docs/PRIVACY.md`. Core: transient in-memory processing; no plaintext, no
reversible form, no hashes of submissions; POST-only transport; redacted 422s
(pydantic `input` stripped); no browser storage; masked input field;
metadata-only analytics; local-only breach demo; rate limiting; HTTPS note
for production.

## 19. Dashboard

Stat cards (Total Analyses, per-classification counts, Average Score) and five
Recharts visualizations: strength distribution, score distribution, most
common weakness types, password length distribution, pattern detection
frequency. It is impossible by construction for the dashboard to reveal a
password — the schema contains no such field. Synthetic demo data seeded via
`scripts/seed_demo_data.py`.

## 20. Testing

69 automated tests (`pytest`): 30 mandated scenarios (empty → analytics
storage), 10 parametrized score-boundary cases, PDF demo calibration
(`123456`→0 VERY WEAK, `Password123!`→WEAK, 16×a→WEAK, `qwerty2026!`→WEAK,
generated→VERY STRONG), 9 API tests (structure, validation 422, rate limit
429, generator), 11 security tests. Result: **69 passed**. Evidence:
`screenshots/22_unit_tests.png`, `screenshots/23_privacy_security_tests.png`,
raw output in `evidence/`.

## 21. Security Testing

Verified automatically: password not stored / not logged / not in database
(dump + hash scan) / not in API response / not in URL / not echoed in errors;
password field semantics; zero localStorage/sessionStorage persistence;
metadata-only analytics; personal-context non-persistence; rate limiting.
Each check is documented with its rationale in `docs/SECURITY_TESTING.md`.

## 22. Results

| Input | Score | Class | Detected |
|---|---|---|---|
| `123456` | 0 | VERY WEAK | common, sequence, numeric run |
| `iloveyou` | 15 | VERY WEAK | common (hard cap) |
| `Password123!` | 38 | WEAK | dictionary, sequence, predictable structure |
| `aaaaaaaaaaaaaaaa` | 35 | WEAK | repeated chars + substring |
| `qwerty2026!` | 35 | WEAK | keyboard, year, structure |
| `P@ssw0rd` | 15 | VERY WEAK | leetspeak → common |
| `P@ssw0rd99` | 44 | MODERATE | leetspeak + dictionary + structure |
| `Tr0p!cal-Driftwood-7829` | 73 | STRONG | minor findings only |
| generated 20-char | 99–100 | VERY STRONG | none |

Dashboard aggregates render correctly over the seeded synthetic dataset;
policy checker and breach demo behave as specified.

## 23. Limitations

- Heuristic scoring cannot perfectly assess human predictability (stated
  openly in the product).
- Small local word lists; English-centric patterns; basic leetspeak map.
- Synthetic demo breach corpus only; guess-resistance labels assume one
  attacker model; demo-grade in-memory rate limiting.

## 24. Future Scope

Mature strength-estimation library integration; true k-anonymity breach
checks; configurable enterprise policies; org-level aggregate reporting (still
password-free); password-manager/SSO concepts; WebAuthn/passkey education;
localization and accessibility improvements.

## 25. Conclusion

The project delivers a complete, executable, privacy-first password strength
analyzer with transparent scoring, specific coaching, defensive generator and
policy utilities, and verifiable privacy guarantees — demonstrating that
modern password assessment requires length, unpredictability, pattern
resistance, common-password checks and context working together, and that
such tooling can itself be built without ever endangering the secrets it
evaluates.
