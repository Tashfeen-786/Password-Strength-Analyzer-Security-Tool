# Testing Strategy

**69 automated tests**, all runnable with:

```bash
python -m pytest tests/ -v          # Windows: scripts\run_tests.bat
```

Synthetic demo passwords only — no real credentials anywhere.

## PDF section 30 — the 30 required scenarios

| # | Scenario | Test |
|---|---|---|
| 1 | Empty password | `test_01_empty_password` |
| 2 | One-character password | `test_02_one_character_password` |
| 3 | Short numeric password | `test_03_short_numeric_password` |
| 4 | Common password | `test_04_common_password`, `test_04b_...` |
| 5 | Long repeated password | `test_05_long_repeated_password` |
| 6 | Lowercase only | `test_06_lowercase_only` |
| 7 | Uppercase only | `test_07_uppercase_only` |
| 8 | Numbers only | `test_08_numbers_only` |
| 9 | Symbols only | `test_09_symbols_only` |
| 10 | Mixed characters | `test_10_mixed_characters` |
| 11 | Sequential numbers | `test_11_sequential_numbers` |
| 12 | Reverse numeric sequence | `test_12_reverse_numeric_sequence` |
| 13 | Sequential letters | `test_13_sequential_letters` |
| 14 | Keyboard sequence | `test_14_keyboard_sequence` |
| 15 | Repeated characters | `test_15_repeated_characters` |
| 16 | Repeated substring | `test_16_repeated_substring` |
| 17 | Common word + number | `test_17_common_word_plus_number` |
| 18 | Word + year | `test_18_word_plus_year` |
| 19 | Personal name overlap | `test_19_personal_name_overlap` |
| 20 | Birth year overlap | `test_20_birth_year_overlap` |
| 21 | Long passphrase-like input | `test_21_long_passphrase_like_input` |
| 22 | Unicode handling | `test_22_unicode_handling` |
| 23 | Space handling | `test_23_space_handling` |
| 24 | Maximum accepted length | `test_24_maximum_length_handling` + API 422 test |
| 25 | Strength-score boundaries | `test_25_score_boundaries` (10 parametrized pairs) |
| 26 | Suggestion generation | `test_26_suggestion_generation`, `test_26b_...` |
| 27 | Secure password generation | `test_27_...`, `test_27b_...` (incl. `secrets`-not-`random` source check) |
| 28 | Password not stored | `test_28_password_not_stored` |
| 29 | Password not logged | `test_29_password_not_logged` |
| 30 | Analytics storage | `test_30_analytics_storage_metadata_only` |

## API tests (`tests/test_api.py`, 9 tests)

Health · analyze structure & privacy marker · context + policy override ·
empty/max-length/too-long handling (200 vs 422) · malformed bodies (422) ·
generator endpoints (200) · generator validation (422) · dashboard stats +
weakness schema & privacy keys · analytics recording flag.

## Security/privacy tests (`tests/test_security_privacy.py`, 11 tests)

See `docs/SECURITY_TESTING.md`.

## Demo calibration (PDF section 29) — verified by tests

| Input | Expected (PDF) | Actual |
|---|---|---|
| `123456` | VERY WEAK | 0 · VERY WEAK ✓ |
| `Password123!` | Weak/Moderate | 38 · WEAK ✓ |
| `aaaaaaaaaaaaaaaa` | Weak | 35 · WEAK ✓ |
| `qwerty2026!` | Weak | 35 · WEAK ✓ |
| generated 20-char | Strong/Very Strong | 99–100 · VERY STRONG ✓ |

Latest run: **69 passed, 0 failed** (evidence in `screenshots/22_unit_tests.png`,
`screenshots/23_privacy_security_tests.png`; raw output in `evidence/`).
