# Security Testing — what was verified and why it matters

All checks run automatically in `tests/test_security_privacy.py`
(`python -m pytest tests/test_security_privacy.py -v`).

| # | Check | Why it matters | Test |
|---|---|---|---|
| 1 | Password is not stored | A stored plaintext password turns the tool into a credential database | `test_password_not_in_database` |
| 2 | Password not in logs | Log files leak: to aggregation services, admins, backups | `test_password_not_in_logs` |
| 3 | Password not in database | Even metadata stores can be breached; minimize blast radius | `test_password_not_in_database` (+ hash scan) |
| 4 | Password not returned in API response | Responses are cached, logged by proxies, shown in dev tools | `test_password_not_in_api_response` |
| 5 | Password not in URL parameters | URLs leak via browser history, access logs, referrers | `test_password_not_accepted_via_url` |
| 6 | Password input is a real password field | Shoulder-surfing protection; browser won't autocomplete-store it | `test_password_input_is_password_type` |
| 7 | Frontend avoids unnecessary persistence | Anything in web storage outlives the session and is readable by any script | `test_frontend_does_not_persist_password` |
| 8 | localStorage contains no password | Same as above | `test_frontend_does_not_persist_password` |
| 9 | sessionStorage contains no password | Same as above | `test_frontend_does_not_persist_password` |
| 10 | Analytics contain only metadata | Analytics pipelines are the classic accidental-leak path | `test_analytics_rows_are_metadata_only`, `test_context_is_never_reflected` |
| 11 | Validation errors redacted | pydantic embeds the offending input (`input` key) in error bodies by default — that would leak the password on a 422 | `test_validation_error_does_not_echo_password` |

Additional automated checks:

- Database dump scan proves no password **and no SHA-1/SHA-256/MD5 hash** of
  the password is persisted.
- Personal context ("Rahul", birth year, org) never appears in FINDINGS rows.
- Rate limiting returns 429 after the demo threshold.
- Full API + hashing behavior covered by `tests/test_api.py` and
  `tests/test_password_analyzer.py`.

Evidence: `screenshots/23_privacy_security_tests.png` (real pytest output),
`evidence/security_tests.txt`.
