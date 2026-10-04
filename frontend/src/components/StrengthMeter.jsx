const CLASS_COLORS = {
  'VERY WEAK': 'var(--very-weak)',
  WEAK: 'var(--weak)',
  MODERATE: 'var(--moderate)',
  STRONG: 'var(--strong)',
  'VERY STRONG': 'var(--very-strong)',
}
const CLASS_RANK = {
  'VERY WEAK': 0, WEAK: 1, MODERATE: 2, STRONG: 3, 'VERY STRONG': 4,
}

export function classColor(c) {
  return CLASS_COLORS[c] || 'var(--muted)'
}

// Segmented real-time strength meter (0-100 score, project-defined bands).
export default function StrengthMeter({ score, classification }) {
  const rank = CLASS_RANK[classification] ?? 0
  const color = CLASS_COLORS[classification] || 'var(--muted)'
  return (
    <div>
      <div className="meter-row">
        <div className="score-big" style={{ color }}>
          {score}<span className="denom">/100</span>
        </div>
        <div className="class-badge" style={{ color }}>{classification}</div>
      </div>
      <div className="meter" aria-label="strength meter">
        {[0, 1, 2, 3, 4].map(i => (
          <div key={i} className={`seg ${i <= rank && score > 0 ? `on c${rank}` : ''}`} />
        ))}
      </div>
      <div className="meter-caption">
        Project-defined bands: 0-20 Very Weak · 21-40 Weak · 41-60 Moderate · 61-80 Strong · 81-100 Very Strong
      </div>
    </div>
  )
}
