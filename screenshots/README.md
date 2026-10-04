# Screenshot / Evidence Checklist (28 items — PDF section 39)

Legend — **Auto/Browser**: captured automatically from the real running app
or from genuine captured command output. **Manual**: account-dependent items
that must be captured by you (never fabricated).

| # | Filename | Description | Type | Status | In ZIP? | If manual — how to capture |
|---|----------|-------------|------|--------|---------|-----------------------------|
| 1 | `01_project_structure.png` | Full project folder tree | Auto (real `tree_snapshot.py` output) | ✅ Generated | Yes | — |
| 2 | `02_architecture.png` | System architecture diagram + privacy boundary | Auto (SVG render of real architecture) | ✅ Generated | Yes | — |
| 3 | `03_analyzer_homepage.png` | Analyzer tab, initial state | Browser (real UI) | ✅ Generated | Yes | — |
| 4 | `04_hidden_password.png` | Masked password field + 👁 Show toggle | Browser (real UI) | ✅ Generated | Yes | — |
| 5 | `05_very_weak_result.png` | `123456` → 0, VERY WEAK | Browser (real analysis) | ✅ Generated | Yes | — |
| 6 | `06_weak_result.png` | `qwerty2026!` → 35, WEAK | Browser (real analysis) | ✅ Generated | Yes | — |
| 7 | `07_moderate_result.png` | `P@ssw0rd99` → 44, MODERATE | Browser (real analysis) | ✅ Generated | Yes | — |
| 8 | `08_strong_result.png` | `Tr0p!cal-Driftwood-7829` → 73, STRONG | Browser (real analysis) | ✅ Generated | Yes | — |
| 9 | `09_very_strong_result.png` | `Zx7!kQ29#vLm4&Rp8wT5` → 100, VERY STRONG | Browser (real analysis) | ✅ Generated | Yes | — |
| 10 | `10_length_analysis.png` | Length bands & metrics (20-char sample) | Browser (real UI) | ✅ Generated | Yes | — |
| 11 | `11_sequence_detection.png` | Sequence findings for `SkyBlue-12345` | Browser (real findings) | ✅ Generated | Yes | — |
| 12 | `12_keyboard_pattern_detection.png` | Keyboard findings for `qwerty2026!` | Browser (real findings) | ✅ Generated | Yes | — |
| 13 | `13_repetition_detection.png` | Repetition findings for `aaaaaaaaaaaaaaaa` | Browser (real findings) | ✅ Generated | Yes | — |
| 14 | `14_common_password_warning.png` | Common-password warning for `iloveyou` | Browser (real findings) | ✅ Generated | Yes | — |
| 15 | `15_security_recommendations.png` | Suggestion list (demo context `John@2026`) | Browser (real suggestions) | ✅ Generated | Yes | — |
| 16 | `16_entropy_explanation.png` | Entropy formula, example, limitation | Browser (Learn tab) | ✅ Generated | Yes | — |
| 17 | `17_password_generator.png` | Generator with real generated output | Browser (real UI) | ✅ Generated | Yes | — |
| 18 | `18_policy_checker.png` | POLICY PASS/FAIL vs strength score | Browser (real UI) | ✅ Generated | Yes | — |
| 19 | `19_analytics_dashboard.png` | Full dashboard (seeded synthetic data) | Browser (real UI) | ✅ Generated | Yes | — |
| 20 | `20_strength_distribution.png` | Strength-distribution chart | Browser (real chart) | ✅ Generated | Yes | — |
| 21 | `21_weakness_chart.png` | Most-common-weakness-types chart | Browser (real chart) | ✅ Generated | Yes | — |
| 22 | `22_unit_tests.png` | 49 analyzer tests, all PASSED | Auto (genuine pytest output) | ✅ Generated | Yes | — |
| 23 | `23_privacy_security_tests.png` | 11 privacy/security tests, all PASSED | Auto (genuine pytest output) | ✅ Generated | Yes | — |
| 24 | `24_api_response.png` | Real POST /api/analyze response | Auto (live API capture) | ✅ Generated | Yes | — |
| 25 | `25_database_schema_no_password.png` | Live schema: **no password field** | Auto (real `.schema` + PRAGMA) | ✅ Generated | Yes | — |
| 26 | `26_github_commits.png` | GitHub commit history | Account-dependent | ⚠ **MANUAL CAPTURE REQUIRED** | No (placeholder not fabricated) | Push to YOUR GitHub (see `docs/GITHUB_GUIDE.md`), open Commits page, capture at 1440×900, save under this name |
| 27 | `27_github_repository.png` | GitHub repository home page | Account-dependent | ⚠ **MANUAL CAPTURE REQUIRED** | No | Open your repo `Password-Strength-Analyzer-Security-Tool`, capture home page, save under this name |
| 28 | `28_readme_preview.png` | README.md preview (actual content) | Auto (real README head) | ✅ Generated | Yes | — |

## Regenerating automatically

```bash
# requires: backend running on :8000 + playwright installed
python scripts/generate_screenshots.py        # items 03–21 (real UI captures)
python scripts/generate_terminal_evidence.py  # items 01, 02, 22–25, 28
```

All screenshots use **synthetic demo passwords only** — never real credentials.
Only items 26–27 require manual capture from your own GitHub account.
