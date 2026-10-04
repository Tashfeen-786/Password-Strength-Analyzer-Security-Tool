import { useEffect, useRef, useState } from 'react'
import { analyzePassword } from '../api.js'
import StrengthMeter from './StrengthMeter.jsx'
import FindingsList from './FindingsList.jsx'

const LAST_RESPONSE_KEY = null // (privacy: nothing is ever persisted)

export default function AnalyzerPage() {
  const [pw, setPw] = useState('')
  const [visible, setVisible] = useState(false) // default: password hidden
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [context, setContext] = useState({ first_name: '', birth_year: '', organization: '' })
  const [minLen, setMinLen] = useState(12)
  const [res, setRes] = useState(null)
  const [state, setState] = useState('idle') // idle | loading | error
  const debounce = useRef(null)

  useEffect(() => {
    if (debounce.current) clearTimeout(debounce.current)
    debounce.current = setTimeout(async () => {
      try {
        setState('loading')
        const policy = minLen !== 12 ? { minimum_length: minLen } : null
        const r = await analyzePassword(pw, context, policy)
        setRes(r)
        setState('idle')
      } catch (e) {
        setState('error')
      }
    }, 250)
    return () => clearTimeout(debounce.current)
  }, [pw, context, minLen])

  const m = res?.metrics
  const policyPassed = res?.policy?.policy_result === 'POLICY PASS'

  return (
    <div>
      <div className="grid-2">
        {/* ---------- input card ---------- */}
        <section className="card">
          <h2>Analyze a password</h2>
          <p className="sub">
            Type a password to analyze it in real time. It is processed in memory only —
            never stored, never logged, never sent to external services.
            Use synthetic demo passwords for this tool.
          </p>

          <label className="fld" htmlFor="pw-input">Password (demo/synthetic only)</label>
          <div className="pw-wrap">
            <input
              id="pw-input"
              type={visible ? 'text' : 'password'}
              autoComplete="new-password"
              placeholder="Type a demo password…"
              value={pw}
              maxLength={128}
              onChange={e => setPw(e.target.value)}
            />
            <button
              type="button"
              className="eye-btn"
              id="toggle-visibility"
              aria-label={visible ? 'Hide password' : 'Show password'}
              onClick={() => setVisible(v => !v)}
            >
              {visible ? '🙈 Hide' : '👁 Show Password'}
            </button>
          </div>

          <details className="advanced" open={showAdvanced}>
            <summary onClick={e => { e.preventDefault(); setShowAdvanced(s => !s) }}>
              Optional demo context &amp; policy (never stored)
            </summary>
            <div className="context-grid">
              <div>
                <label className="fld">First name (demo)</label>
                <input type="text" maxLength={64} placeholder="e.g. Rahul"
                  value={context.first_name}
                  onChange={e => setContext(c => ({ ...c, first_name: e.target.value }))} />
              </div>
              <div>
                <label className="fld">Birth year (demo)</label>
                <input type="text" maxLength={4} placeholder="e.g. 1999"
                  value={context.birth_year}
                  onChange={e => setContext(c => ({ ...c, birth_year: e.target.value }))} />
              </div>
              <div>
                <label className="fld">Company / college (demo)</label>
                <input type="text" maxLength={64} placeholder="e.g. Contoso"
                  value={context.organization}
                  onChange={e => setContext(c => ({ ...c, organization: e.target.value }))} />
              </div>
            </div>
            <div style={{ marginTop: 14, maxWidth: 260 }}>
              <label className="fld">Policy minimum length</label>
              <select value={minLen} onChange={e => setMinLen(Number(e.target.value))}>
                {[8, 10, 12, 14, 16, 20].map(n => (
                  <option key={n} value={n}>{n} characters</option>
                ))}
              </select>
            </div>
          </details>

          <div className="notice mt">
            🔒 Privacy: this field is a real password field. Your input is analyzed
            transiently via POST and is never written to browser storage, URLs or logs.
          </div>
        </section>

        {/* ---------- result card ---------- */}
        <section className="card" id="result-card">
          <h2>Strength result</h2>
          <p className="sub">Real-time score, classification and pattern analysis.</p>
          {state === 'error' && <div className="err">⚠ Could not reach the analysis API.</div>}
          {!res && state !== 'error' && <div className="loading">Waiting for input…</div>}
          {res && (
            <div>
              <StrengthMeter score={res.score} classification={res.classification} />
              <div className="metric-grid mt">
                <div className="metric">
                  <div className="m-label">Length</div>
                  <div className="m-value">{m.length.length} chars — {m.length.band}</div>
                  <div className="m-note">
                    Recommended minimum 12 {m.length.meets_recommended_minimum_12
                      ? <span className="pass">✓</span> : <span className="fail">✗</span>}
                  </div>
                </div>
                <div className="metric">
                  <div className="m-label">Character diversity</div>
                  <div className="m-value">{m.characters.character_type_count}/4 classes</div>
                  <div className="m-note">
                    {m.characters.has_lowercase ? 'lower ✓ ' : 'lower ✗ '}
                    {m.characters.has_uppercase ? 'upper ✓ ' : 'upper ✗ '}
                    {m.characters.has_digits ? 'digit ✓ ' : 'digit ✗ '}
                    {m.characters.has_symbols ? 'symbol ✓' : 'symbol ✗'}
                  </div>
                </div>
                <div className="metric">
                  <div className="m-label">Unique-character ratio</div>
                  <div className="m-value">
                    {m.characters.unique_character_count}/{m.characters.length} ({Math.round(m.characters.unique_character_ratio * 100)}%)
                  </div>
                  <div className="m-note">Low ratios signal repetition.</div>
                </div>
                <div className="metric">
                  <div className="m-label">Entropy estimate</div>
                  <div className="m-value">{m.entropy.entropy_bits} bits</div>
                  <div className="m-note">L × log₂(N) = {m.entropy.length} × log₂({m.entropy.pool_size})</div>
                </div>
                <div className="metric">
                  <div className="m-label">Guess resistance</div>
                  <div className="m-value" style={{ fontSize: 14 }}>{m.guess_resistance}</div>
                  <div className="m-note">Educational estimate only — not a guarantee.</div>
                </div>
                <div className="metric">
                  <div className="m-label">Breach check (demo)</div>
                  <div className="m-value" style={{ fontSize: 14 }}>
                    {res.breach_check?.found
                      ? <span className="fail">⚠ Found in demo breach list</span>
                      : <span className="pass">✓ Not in demo breach list</span>}
                  </div>
                  <div className="m-note">Local synthetic corpus of {res.breach_check?.corpus_size} hashes.</div>
                </div>
              </div>
              <p className="sub" style={{ marginTop: 14 }}>{res.disclaimer}</p>
            </div>
          )}
        </section>
      </div>

      {res && pw.length > 0 && (
        <div className="grid-2 mt">
          <section className="card" id="findings-card">
            <h3>Findings ({res.findings.length})</h3>
            <FindingsList findings={res.findings} />
          </section>

          <section className="card" id="suggestions-card">
            <h3>Security recommendations</h3>
            {res.suggestions.map((s, i) => (
              <div className="suggestion" key={i}><span className="bulb">💡</span>{s}</div>
            ))}
          </section>
        </div>
      )}

      {res && res.policy && pw.length > 0 && (
        <div className="grid-2 mt">
          <section className="card">
            <h3>Score breakdown (transparent scoring)</h3>
            <table className="rules">
              <thead>
                <tr><th>Signal</th><th>Points</th></tr>
              </thead>
              <tbody>
                {Object.entries(m.score_breakdown.contributions).map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</td>
                    <td className="pass">+{v}</td>
                  </tr>
                ))}
                {Object.entries(m.score_breakdown.penalties).map(([k, v]) => (
                  <tr key={k}>
                    <td style={{ textTransform: 'capitalize' }}>Penalty: {k.replace(/_/g, ' ')}</td>
                    <td className="fail">−{v}</td>
                  </tr>
                ))}
                <tr>
                  <td><b>Final (cap 0-100{cappedNote(m)})</b></td>
                  <td><b>{res.score}</b></td>
                </tr>
              </tbody>
            </table>
            <p className="sub" style={{ marginTop: 10 }}>
              Passwords like <code className="k">Password123!</code> show why composition rules alone are not enough.
            </p>
          </section>

          <section className="card" id="policy-card">
            <h3>Password policy check</h3>
            <div className={`policy-verdict ${policyPassed ? 'pass' : 'fail'}`}>
              {res.policy.policy_result}
            </div>
            <table className="rules">
              <thead>
                <tr><th>Rule</th><th>Result</th><th>Detail</th></tr>
              </thead>
              <tbody>
                {res.policy.rules.map((r, i) => (
                  <tr key={i}>
                    <td>{r.rule}</td>
                    <td><span className={`pill ${r.passed ? 'ok' : 'no'}`}>{r.passed ? 'PASS' : 'FAIL'}</span></td>
                    <td style={{ color: 'var(--muted)' }}>{r.detail}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="sub" style={{ marginTop: 10 }}>
              POLICY PASS/FAIL is separate from the STRENGTH SCORE: a password can comply
              with policy and still be predictable (and vice versa).
            </p>
          </section>
        </div>
      )}
    </div>
  )
}

function cappedNote(m) {
  const notes = []
  if (m.score_breakdown.breach_cap_applied) notes.push('breach cap applied')
  return notes.length ? `, ${notes.join(', ')}` : ''
}
