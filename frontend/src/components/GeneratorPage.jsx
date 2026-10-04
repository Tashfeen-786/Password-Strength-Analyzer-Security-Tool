import { useState } from 'react'
import { generateCredential } from '../api.js'

// Secure password generator (defensive feature).
// Generated values are demo output — never stored, never logged.
export default function GeneratorPage() {
  const [mode, setMode] = useState('password')
  const [length, setLength] = useState(16)
  const [opts, setOpts] = useState({ uppercase: true, lowercase: true, numbers: true, symbols: true })
  const [words, setWords] = useState(4)
  const [out, setOut] = useState(null)
  const [copied, setCopied] = useState(false)
  const [err, setErr] = useState('')

  async function generate() {
    setErr('')
    setCopied(false)
    try {
      const body = mode === 'password'
        ? { mode, length, ...opts }
        : { mode, words, separator: '-' }
      const r = await generateCredential(body)
      setOut(r)
    } catch (e) {
      setErr('Generation failed — is the backend running?')
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(out.generated)
      setCopied(true)
    } catch { setErr('Clipboard unavailable in this browser context.') }
  }

  const toggle = k => setOpts(o => ({ ...o, [k]: !o[k] }))

  return (
    <div className="grid-2">
      <section className="card">
        <h2>Secure password generator</h2>
        <p className="sub">
          Uses Python's <code className="k">secrets</code> module (cryptographically secure
          randomness) — <b>not</b> <code className="k">random</code>. Generated values are
          returned once and never stored or logged.
        </p>

        <label className="fld">Mode</label>
        <div className="btn-row" style={{ marginBottom: 16 }}>
          <button className={`btn ${mode === 'password' ? '' : 'ghost'}`} onClick={() => setMode('password')}>
            Random password
          </button>
          <button className={`btn ${mode === 'passphrase' ? '' : 'ghost'}`} onClick={() => setMode('passphrase')}>
            Passphrase
          </button>
        </div>

        {mode === 'password' ? (
          <>
            <label className="fld">Length</label>
            <div className="btn-row" style={{ marginBottom: 16 }}>
              {[16, 20, 24].map(n => (
                <button key={n} className={`btn ${length === n ? '' : 'ghost'}`} onClick={() => setLength(n)}>
                  {n}
                </button>
              ))}
            </div>
            <label className="fld">Character classes</label>
            <div className="btn-row">
              {[['lowercase', 'abc'], ['uppercase', 'ABC'], ['numbers', '123'], ['symbols', '#$&']].map(([k, label]) => (
                <button key={k} className={`btn ${opts[k] ? '' : 'ghost'}`} onClick={() => toggle(k)}>
                  {opts[k] ? '✓ ' : ''}{label}
                </button>
              ))}
            </div>
          </>
        ) : (
          <>
            <label className="fld">Words</label>
            <div className="btn-row" style={{ marginBottom: 16 }}>
              {[3, 4, 5, 6].map(n => (
                <button key={n} className={`btn ${words === n ? '' : 'ghost'}`} onClick={() => setWords(n)}>
                  {n} words
                </button>
              ))}
            </div>
            <div className="notice">
              Passphrase strength comes from the <b>number and randomness</b> of the words,
              not from word obscurity (see the Learn tab for password vs passphrase).
            </div>
          </>
        )}

        <div className="btn-row mt">
          <button className="btn" id="generate-btn" onClick={generate}>Generate</button>
          {out && <button className="btn ghost" id="copy-btn" onClick={copy}>{copied ? '✓ Copied' : 'Copy'}</button>}
          {out && <button className="btn ghost" onClick={generate}>↻ Regenerate</button>}
        </div>

        {out && <div className="gen-out" id="generated-value">{out.generated}</div>}
        {err && <div className="err mt">{err}</div>}
      </section>

      <section className="card">
        <h3>Why <code className="k">secrets</code> and not <code className="k">random</code>?</h3>
        <p className="sub" style={{ lineHeight: 1.7 }}>
          Python's <code className="k">random</code> is a deterministic pseudo-random generator
          designed for simulation: given enough output its state can be reconstructed and future
          "random" values predicted. <code className="k">secrets</code> draws from the operating
          system's cryptographically secure random source (CSPRNG), which is the documented,
          recommended source for security-sensitive randomness such as passwords and tokens.
        </p>
        <div className="notice">
          ℹ️ The generator guarantees at least one character from every enabled class, then fills
          and securely shuffles the remainder. Nothing about generated values is persisted —
          treat them as demonstration output and never reuse the same password across accounts.
        </div>
        <div className="notice warn mt">
          ⚠ A password manager is the recommended way to generate and store unique passwords
          for real accounts.
        </div>
      </section>
    </div>
  )
}
