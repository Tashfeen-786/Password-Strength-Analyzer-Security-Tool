const SEV_ICON = {
  critical: '⛔', high: '⚠️', medium: '⚠️', low: 'ℹ️', info: '✅',
}

export default function FindingsList({ findings }) {
  if (!findings || findings.length === 0) {
    return (
      <div className="finding sev-info">
        <div className="icon">✅</div>
        <div>
          <div className="ftitle">No weaknesses detected</div>
          <div className="fdetail">
            No common-password, dictionary, sequence, keyboard, repetition,
            date or personal-info patterns were detected by this tool's checks.
            (No tool can guarantee strength — keep passwords unique.)
          </div>
        </div>
      </div>
    )
  }
  return (
    <div>
      {findings.map((f, i) => (
        <div className={`finding sev-${f.severity}`} key={i}>
          <div className="icon">{SEV_ICON[f.severity] || 'ℹ️'}</div>
          <div>
            <div className="ftitle">{f.title}</div>
            <div className="fdetail">{f.detail || f.description}</div>
          </div>
        </div>
      ))}
    </div>
  )
}
