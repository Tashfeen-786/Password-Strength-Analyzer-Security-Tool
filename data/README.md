# Data Files (Educational / Synthetic Only)

This directory contains **small, educational, synthetic** datasets used by the
Password Strength Analyzer. They contain **no real leaked credentials** and no
personal data.

## `common_passwords.txt`
A short, curated list of widely known, publicly documented weak passwords
(e.g. `123456`, `qwerty`, `password`). These strings appear in every public
"top common passwords" ranking and security textbook. Used by
`backend/services/common_checker.py` for the common-password check.

## `dictionary_words.txt`
A small list of common English words used for the dictionary / common-word
detection signal. Words of length >= 4 found inside a password (after splitting
on separators) are flagged.

## `breached_sha1.txt`
**Synthetic demo breach corpus.** Upper-case hex SHA-1 hashes of a handful of
invented demo strings (see `backend/services/breach_checker.py` docstring and
`docs/PRIVACY.md`). It exists only to demonstrate, locally, how "has this
password appeared in a breach corpus?" detection works **without ever sending
a password to an external service**.

> Production equivalent: a k-anonymity service (e.g. Pwned-Passwords style,
> where only the first 5 hex characters of a SHA-1 hash leave the client).
> This project deliberately does **not** call external services by default.
