// API client — same-origin relative URLs only.
// PRIVACY: the password leaves this page only via a POST body to the local
// analysis API; it is never put in a URL, never written to web storage,
// and never logged to the console.

export async function analyzePassword(password, context, policy) {
  const body = { password }
  if (context && (context.first_name || context.birth_year || context.organization)) {
    body.context = context
  }
  if (policy) body.policy = policy
  const res = await fetch('/api/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`Analysis failed (${res.status})`)
  return res.json()
}

export async function generateCredential(options) {
  const res = await fetch('/api/generate-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options),
  })
  if (!res.ok) throw new Error(`Generation failed (${res.status})`)
  return res.json()
}

export async function fetchDashboardStats() {
  const res = await fetch('/api/dashboard/stats')
  if (!res.ok) throw new Error(`Stats failed (${res.status})`)
  return res.json()
}

export async function fetchWeaknesses() {
  const res = await fetch('/api/analytics/weaknesses')
  if (!res.ok) throw new Error(`Weaknesses failed (${res.status})`)
  return res.json()
}
