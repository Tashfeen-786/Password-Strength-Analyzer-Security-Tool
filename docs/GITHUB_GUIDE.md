# GitHub Upload Guide

> **Integrity note:** this project does NOT ship pre-fabricated GitHub
> screenshots. Items 26 (`26_github_commits.png`) and 27
> (`27_github_repository.png`) of the evidence checklist are marked
> **MANUAL CAPTURE REQUIRED** — capture them from YOUR account after you push.

## 1. Create the repository

- Name: **`Password-Strength-Analyzer-Security-Tool`**
- Description: *"Privacy-focused cybersecurity tool for evaluating password
  strength using length, predictability, common-password checks, pattern
  analysis, entropy concepts, and personalized security recommendations."*
- Topics: `cybersecurity` `password-security` `password-strength`
  `application-security` `python` `flask` `fastapi` `secure-coding` `iam`
  `security-awareness` `defensive-security`
- Public, **do not** include any secrets (this project needs none).

## 2. Push

From inside the project folder (the folder containing this guide):

```bash
git init
git add .
git commit -m "Initialize password strength analyzer"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

## 3. Recommended follow-up commits (practice a clean history)

```bash
git commit -m "Create password analyzer architecture"
git commit -m "Implement password length analysis"
git commit -m "Add character diversity analysis"
git commit -m "Implement common password detection"
git commit -m "Add sequence and keyboard pattern detection"
git commit -m "Implement repetition detection"
git commit -m "Add entropy estimation"
git commit -m "Build password strength scoring engine"
git commit -m "Implement security suggestion engine"
git commit -m "Add secure password generator"
git commit -m "Build real-time password strength meter"
git commit -m "Add privacy-safe analytics dashboard"
git commit -m "Implement automated security tests"
git commit -m "Complete README and documentation"
```

## 4. What is git-ignored (and why)

`.gitignore` excludes: `__pycache__/`, `.venv/`, `node_modules/`,
`frontend/dist/` (build output — rebuilt by `npm run build`), `.env`,
and `backend/analytics.db` (runtime data). All of these can be regenerated
locally; none belongs in version control.

## 5. After pushing (manual evidence)

1. Open your repo → capture the repository home →
   `screenshots/27_github_repository.png`
2. Open the Commits page → capture → `screenshots/26_github_commits.png`
3. Add a screenshot or two from `screenshots/` into the README if desired
   (two are already embedded by relative path).
