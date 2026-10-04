const RULES = [
  ['Use unique passwords for every account', 'One breach must never cascade into your other accounts (credential stuffing).'],
  ['Prefer longer passwords and passphrases', 'Length grows the guessing search space faster than any symbol rule.'],
  ['Avoid predictable personal information', 'Names, birthdays, pets and teams are exactly what attackers try first.'],
  ['Avoid common passwords', '“123456”, “qwerty”, “letmein” are in every cracking list on earth.'],
  ['Never reuse passwords', 'Reuse is how one weak site compromises your important accounts.'],
  ['Use a password manager', 'It generates and remembers unique passwords so you don’t have to.'],
  ['Enable MFA everywhere possible', 'A second factor protects you even when a password leaks.'],
  ['Never share your passwords', 'No legitimate service will ever ask you for your password.'],
  ['Be cautious of phishing', 'Check the sender and URL; a strong password typed into a fake site is a lost password.'],
  ['Change passwords when compromise is suspected', 'Rotate on suspected or confirmed compromise — not on an arbitrary calendar.'],
]

export default function LearnPage() {
  return (
    <div className="learn">
      <section className="card">
        <h2>Password vs Passphrase</h2>
        <p>
          A <b>password</b> is usually one short word with substitutions and symbols — hard for
          humans to remember, easy for machines with the right rules. A <b>passphrase</b> is a
          sequence of <i>randomly selected</i> words (e.g. <code className="k">velvet-galaxy-harbor-orchid</code>
          {' '}— fictional demonstration example, do not reuse). Because its strength comes from
          the <i>number and randomness of words</i>, a passphrase can be both easier to remember
          and harder to guess.
        </p>
        <div className="notice warn">
          ⚠ Never use famous quotes, lyrics or predictable phrases as passphrases — attackers
          rule-test those too. Random selection is the whole point.
        </div>
      </section>

      <section className="card mt" id="entropy-explainer">
        <h2>What is password entropy?</h2>
        <div className="formula">Entropy ≈ L × log₂(N)</div>
        <p>
          <b>L</b> is the password length and <b>N</b> is the size of the character pool
          (26 lowercase, +26 uppercase, +10 digits, +33 symbols…). This estimates the size of
          the theoretical search space — <i>if</i> every character were chosen uniformly at random.
        </p>
        <table className="rules">
          <thead><tr><th>Demo password</th><th>L</th><th>Pool N</th><th>Theoretical entropy</th><th>Reality</th></tr></thead>
          <tbody>
            <tr><td><code className="k">Password123!</code></td><td>12</td><td>95</td><td>~78.8 bits</td>
              <td className="fail">Predictable — common word + sequence</td></tr>
            <tr><td>random 16-char generated</td><td>16</td><td>95</td><td>~105.1 bits</td>
              <td className="pass">Estimate meaningful — selection was random</td></tr>
          </tbody>
        </table>
        <p className="sub" style={{ marginTop: 12 }}>
          <b>Limitation:</b> human-chosen passwords are not random, so theoretical entropy is
          optimistic for them. This tool therefore combines the entropy estimate with pattern,
          common-password and context analysis rather than trusting entropy alone.
        </p>
      </section>

      <section className="card mt">
        <h2>10 Password Security Rules</h2>
        {RULES.map(([title, why], i) => (
          <div className="rule-item" key={i}>
            <div className="num">{i + 1}</div>
            <div><b>{title}</b><div className="sub" style={{ margin: '3px 0 0' }}>{why}</div></div>
          </div>
        ))}
      </section>

      <div className="grid-2 mt">
        <section className="card">
          <h2>How passwords are stored (concepts)</h2>
          <p>
            Production systems must never store plaintext passwords. They store a <b>salted,
            stretched hash</b>: <code className="k">password → salt → hashing function → stored hash</code>.
            Verification re-computes the hash of the login attempt and compares — the original
            password is never needed or recovered.
          </p>
          <p>
            <b>Hashing ≠ encryption.</b> Encryption is reversible with a key; password hashing is
            one-way verification. Use dedicated, deliberately slow password-hashing functions —
            <b> Argon2id</b> (preferred), <b>bcrypt</b>, <b>scrypt</b> or <b>PBKDF2</b> — never a fast
            general-purpose hash alone. This project ships a standalone educational PBKDF2 demo
            (<code className="k">scripts/hashing_demo.py</code>, synthetic passwords only).
          </p>
        </section>
        <section className="card">
          <h2>Beyond the password</h2>
          <p>
            Password strength is only one layer of authentication security. Real-world login
            security also relies on <b>MFA</b>, <b>rate limiting</b>, <b>secure password hashing</b>,
            <b> account lockout / abuse protection</b>, <b>session security</b>, <b>phishing
            protection</b> and <b>monitoring</b>. Even a very strong password cannot, by itself,
            defend against a phishing page or a reused-password breach.
          </p>
          <div className="notice">
            Guess-resistance numbers shown by this tool are “educational estimates only”: real
            resistance depends on the attacker model, password predictability, the hashing
            algorithm and work factor, rate limiting, and online vs offline scenarios.
          </div>
        </section>
      </div>
    </div>
  )
}
