# Interview Preparation — 10 Questions & Answers

**1. Explain your project.**

I developed a Password Strength Analyzer & Security Suggestion Tool that
evaluates passwords using multiple security factors instead of checking only
whether they contain uppercase letters, lowercase letters, numbers, and
symbols. The system analyzes length, character diversity, repeated patterns,
sequential characters, keyboard patterns, common-password matches, predictable
word-number combinations, leetspeak variants, and optional personal-information
overlap. It also provides an entropy-style estimate and combines the results
into a strength score from 0 to 100 with classification from VERY WEAK to
VERY STRONG. Based on detected weaknesses, the application generates specific
security recommendations. A major privacy feature is that submitted passwords
are analyzed in memory and are never stored in the database or application
logs — I verified that with dedicated privacy tests.

**2. How does your password strength analyzer determine whether a password is strong?**

My analyzer uses multiple signals. Length provides an important positive
contribution (up to 35 of the 100 points), while character variety and
unique-character ratio provide additional information. The system then checks
whether the password contains predictable patterns such as common passwords,
numeric sequences, keyboard walks, repeated characters, repeated substrings,
common word-number or word-year combinations, leetspeak-normalized forms, or
user-provided personal information. Positive and negative signals are combined
into a transparent score between 0 and 100 — the UI shows exactly which
signals earned or lost points. This is more useful than simply checking
whether four character categories are present.

**3. What is password entropy?**

Password entropy describes the uncertainty, or theoretical search space,
associated with a password-generation process. The simplified estimate I use,
`Entropy ≈ L × log₂(N)`, multiplies length by the log of the assumed character
pool. However, that calculation can be misleading for human-created passwords
because it assumes characters are selected randomly. `Password123!` looks
diverse and gets an optimistic ~79 bits, yet is highly predictable. Therefore
in my project theoretical entropy is only one signal, combined with pattern
and common-password analysis — and the UI explains that limitation explicitly.

**4. Why is `Password123!` not necessarily a strong password?**

It contains uppercase and lowercase letters, numbers, and a symbol, so a
simple composition checker accepts it. But it is built from an extremely
predictable word followed by a common numeric sequence and symbol — cracking
rules test that shape immediately. My analyzer detects the dictionary word,
the `123` sequence and the predictable word-plus-number structure, so it
classifies it WEAK (38/100) instead of accepting it. This demonstrates why
strength should consider predictability, common patterns and length rather
than composition rules alone.

**5. What is the difference between hashing and encryption?**

Encryption is designed to be reversible when the correct decryption key is
available. Password hashing is designed for one-way verification. In a
properly designed authentication system, the server stores a password hash
produced by an appropriate password-hashing function rather than the
plaintext password. During login, the submitted password is processed through
the same verification procedure and compared with the stored result — the
application never needs to recover the original password. My project includes
a standalone educational PBKDF2 demonstration of exactly this flow.

**6. What is salting, and why is it important for password storage?**

A salt is a unique random value incorporated into password hashing. It
ensures two users with the same password don't end up with identical stored
representations, and it makes large-scale precomputed lookup attacks (rainbow
tables) impractical. In my hashing demo, hashing the same synthetic password
twice produces two completely different stored strings, yet both verify
correctly — that visibly demonstrates salting. Modern password-hashing
libraries manage salts internally; my analyzer itself doesn't store submitted
passwords at all.

**7. Why shouldn't passwords be stored using a fast general-purpose hash alone?**

General-purpose hashes like MD5, SHA-1 or SHA-256 are designed for speed,
which is great for integrity checks but dangerous for password storage: if a
password database leaks, fast verification enables billions of guesses per
second offline. Password storage uses dedicated, deliberately expensive
functions — Argon2id (currently preferred), bcrypt, scrypt, or PBKDF2 — with
tunable work factors so each guess is costly. My educational demo uses PBKDF2
with 600,000 iterations to illustrate the key-stretching idea.

**8. How did you protect user privacy in this project?**

The password is processed only for the immediate analysis and is not saved in
plaintext, logs, localStorage, sessionStorage, analytics, or database records.
The API does not return the submitted password, and validation errors are
redacted so a 422 can't echo it back. If analytics are enabled, I store only
non-secret metadata — password length, strength classification, score, and
the number of detected weakness categories — and the findings rows contain
only generic descriptions. I wrote 11 automated privacy tests that prove each
of these properties, including scanning a full database dump for both the
password and its hashes. In production I would also require HTTPS.

**9. Is a strong password enough to secure an account?**

No. Password strength is only one layer of authentication security. A secure
system also uses MFA where appropriate, secure password hashing, rate
limiting, account lockout and abuse protection, session security, monitoring,
phishing defenses, and safe recovery mechanisms. Users should also avoid
password reuse — a strong password reused across multiple services still
creates risk if one of those services is compromised. That's why my
suggestions always include enabling MFA and using a password manager.

**10. How would you improve this project in the future?**

I would integrate a mature password-strength estimation library as a
comparison signal, support configurable organizational password policies, and
add true privacy-preserving k-anonymity checks against known-compromised
password datasets. I could also add password-manager education, MFA and SSO
guidance, enterprise IAM integration concepts, and passkey/WebAuthn awareness.
For organizations, I could provide aggregate security-awareness reporting —
still ensuring users' actual passwords are never collected or stored.
