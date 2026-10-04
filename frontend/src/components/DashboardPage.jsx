import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer,
  Tooltip, XAxis, YAxis, Legend,
} from 'recharts'
import { fetchDashboardStats, fetchWeaknesses } from '../api.js'
import { classColor } from './StrengthMeter.jsx'

const CLASS_ORDER = ['VERY WEAK', 'WEAK', 'MODERATE', 'STRONG', 'VERY STRONG']
const CLASS_HEX = {
  'VERY WEAK': '#ef4444', WEAK: '#f97316', MODERATE: '#eab308',
  STRONG: '#22c55e', 'VERY STRONG': '#2dd4bf',
}
const NICE = {
  sequential_pattern: 'Sequences', keyboard_pattern: 'Keyboard patterns',
  repeated_characters: 'Repeated chars', repeated_substring: 'Repeated substrings',
  dictionary_word: 'Dictionary words', common_password: 'Common passwords',
  predictable_structure: 'Word+number', year_date_pattern: 'Years/dates',
  numeric_run: 'Numeric runs', leetspeak_substitution: 'Leetspeak',
  personal_info_name: 'Name in password', personal_info_year: 'Birth year',
  personal_info_org: 'Organization', breach_exposure: 'Breach (demo)',
  empty_password: 'Empty password',
}
const nice = t => NICE[t] || t.replace(/_/g, ' ')

const tooltipStyle = {
  contentStyle: { background: '#0e1730', border: '1px solid #1d2c52', borderRadius: 10 },
  labelStyle: { color: '#e6edf7' }, itemStyle: { color: '#9fd8e8' },
}

export default function DashboardPage() {
  const [stats, setStats] = useState(null)
  const [weak, setWeak] = useState(null)
  const [err, setErr] = useState('')

  async function load() {
    try {
      setErr('')
      const [s, w] = await Promise.all([fetchDashboardStats(), fetchWeaknesses()])
      setStats(s); setWeak(w)
    } catch (e) { setErr('Could not load analytics. Is the backend running?') }
  }
  useEffect(() => { load() }, [])

  if (err) return <section className="card"><div className="err">{err}</div>
    <div className="btn-row mt"><button className="btn" onClick={load}>Retry</button></div></section>
  if (!stats || !weak) return <section className="card"><div className="loading">Loading dashboard…</div></section>

  const classData = CLASS_ORDER.map(c => ({ name: c, value: stats.classifications[c] || 0 }))
  const weaknessData = weak.weakness_types.slice(0, 10)
    .map(w => ({ name: nice(w.type), count: w.count }))
  const patternData = weak.pattern_frequency
    .map(p => ({ name: nice(p.type), count: p.count }))
  const lengthData = stats.length_distribution.map(l => ({ length: l.length, count: l.n }))
  const nonEmpty = stats.total_analyses > 0

  return (
    <div>
      <section className="card">
        <h2>Analytics dashboard</h2>
        <p className="sub">
          Privacy-safe aggregate statistics only. The dashboard stores and displays
          no passwords — only scores, classifications, lengths and weakness categories.
        </p>
        <div className="grid-3" style={{ gridTemplateColumns: 'repeat(7, 1fr)' }}>
          <div className="stat-card"><div className="n" style={{ color: 'var(--accent)' }}>{stats.total_analyses}</div><div className="l">Total Analyses</div></div>
          {CLASS_ORDER.map(c => (
            <div className="stat-card" key={c}>
              <div className="n" style={{ color: CLASS_HEX[c] }}>{stats.classifications[c] || 0}</div>
              <div className="l">{c}</div>
            </div>
          ))}
          <div className="stat-card"><div className="n" style={{ color: 'var(--accent-2)' }}>{stats.average_score}</div><div className="l">Average Score</div></div>
        </div>
      </section>

      {!nonEmpty && (
        <div className="notice mt">No analyses recorded yet. Run a few analyses from the
        Analyzer tab (or <code className="k">scripts/seed_demo_data.py</code> for synthetic demo data).</div>
      )}

      <div className="grid-2 mt">
        <div className="chart-box" id="chart-strength-distribution">
          <h4>1 · Strength Distribution</h4>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={classData} dataKey="value" nameKey="name" innerRadius={55}
                   outerRadius={90} paddingAngle={2} strokeWidth={0}>
                {classData.map(d => <Cell key={d.name} fill={CLASS_HEX[d.name]} />)}
              </Pie>
              <Tooltip {...tooltipStyle} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box" id="chart-score-distribution">
          <h4>2 · Score Distribution (0–100 bands)</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={stats.score_distribution}>
              <CartesianGrid stroke="#16234a" strokeDasharray="3 3" />
              <XAxis dataKey="band" tick={{ fill: '#8da2c0', fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fill: '#8da2c0', fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="count" fill="#22d3ee" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box" id="chart-weakness-types">
          <h4>3 · Most Common Weakness Types</h4>
          <ResponsiveContainer width="100%" height={Math.max(240, weaknessData.length * 34)}>
            <BarChart data={weaknessData} layout="vertical">
              <CartesianGrid stroke="#16234a" strokeDasharray="3 3" />
              <XAxis type="number" allowDecimals={false} tick={{ fill: '#8da2c0', fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={130} tick={{ fill: '#8da2c0', fontSize: 11.5 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="count" fill="#fb7185" radius={[0, 5, 5, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box" id="chart-length-distribution">
          <h4>4 · Password Length Distribution</h4>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={lengthData}>
              <CartesianGrid stroke="#16234a" strokeDasharray="3 3" />
              <XAxis dataKey="length" tick={{ fill: '#8da2c0', fontSize: 11 }} label={{ value: 'length (chars)', position: 'insideBottom', offset: -2, fill: '#8da2c0', fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fill: '#8da2c0', fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="count" fill="#34d399" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-box" id="chart-pattern-frequency" style={{ gridColumn: '1 / -1' }}>
          <h4>5 · Pattern Detection Frequency</h4>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={patternData}>
              <CartesianGrid stroke="#16234a" strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: '#8da2c0', fontSize: 11.5 }} />
              <YAxis allowDecimals={false} tick={{ fill: '#8da2c0', fontSize: 11 }} />
              <Tooltip {...tooltipStyle} />
              <Bar dataKey="count" radius={[5, 5, 0, 0]}>
                {patternData.map((d, i) => (
                  <Cell key={d.name} fill={['#22d3ee', '#818cf8', '#f472b6', '#fbbf24', '#34d399', '#fb7185', '#a3e635'][i % 7]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <p className="footer-note">
        {stats.privacy_note} Synthetic demo data is used for demonstration.
      </p>
    </div>
  )
}
