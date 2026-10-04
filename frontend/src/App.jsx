import { useState } from 'react'
import AnalyzerPage from './components/AnalyzerPage.jsx'
import GeneratorPage from './components/GeneratorPage.jsx'
import DashboardPage from './components/DashboardPage.jsx'
import LearnPage from './components/LearnPage.jsx'

const TABS = [
  { id: 'analyzer', label: 'Analyzer' },
  { id: 'generator', label: 'Generator' },
  { id: 'dashboard', label: 'Dashboard' },
  { id: 'learn', label: 'Learn Security' },
]

function BrandMark() {
  return (
    <div className="brand-badge" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" stroke="#eafcff" strokeWidth="2"
           strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        <path d="M9 12l2 2 4-4" />
      </svg>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('analyzer')
  return (
    <div className="app-shell">
      <header className="topbar">
        <BrandMark />
        <div className="brand">
          <h1>Password Strength Analyzer &amp; Security Suggestion Tool</h1>
          <small>Defensive Cybersecurity Project · Privacy-First · In-Memory Analysis</small>
        </div>
      </header>

      <nav className="nav">
        {TABS.map(t => (
          <button key={t.id} className={tab === t.id ? 'active' : ''}
                  onClick={() => setTab(t.id)} id={`tab-${t.id}`}>
            {t.label}
          </button>
        ))}
      </nav>

      <main>
        {tab === 'analyzer' && <AnalyzerPage />}
        {tab === 'generator' && <GeneratorPage />}
        {tab === 'dashboard' && <DashboardPage />}
        {tab === 'learn' && <LearnPage />}
      </main>

      <footer className="footer-note">
        Educational project. Passwords are analyzed transiently in memory and are never
        stored, logged, or transmitted to external services. Strength scores are
        project-defined educational estimates, not universal security standards.
        <br />Only synthetic demo passwords were used for development, testing and screenshots.
      </footer>
    </div>
  )
}
