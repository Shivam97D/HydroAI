import React, { useEffect, useState, useCallback } from 'react'
import { useStore } from '../store/useStore'
import styles from './SiteConfigPage.module.css'

const BASE = import.meta.env.VITE_API_URL ?? ''

interface SiteConfig {
  check_interval_hours: number
  alerts_enabled: boolean
  last_run: string | null
  next_run: string | null
}

const INTERVALS = [
  { value: 1,  label: 'Every hour' },
  { value: 3,  label: 'Every 3 hours' },
  { value: 6,  label: 'Every 6 hours' },
  { value: 12, label: 'Every 12 hours' },
  { value: 24, label: 'Every 24 hours (daily)' },
]

function authHeaders(token: string | null) {
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }
}

function fmtTime(iso: string | null) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}

export default function SiteConfigPage() {
  const { authUser, authToken, setView } = useStore()
  const [config, setConfig] = useState<SiteConfig | null>(null)
  const [interval, setIntervalVal] = useState(6)
  const [alertsEnabled, setAlertsEnabled] = useState(true)
  const [saving, setSaving] = useState(false)
  const [triggering, setTriggering] = useState(false)
  const [saveMsg, setSaveMsg] = useState('')
  const [subCount, setSubCount] = useState<number | null>(null)
  const [error, setError] = useState('')

  // Redirect non-admins
  useEffect(() => {
    if (!authUser || authUser.role !== 'admin') {
      setView('dashboard')
    }
  }, [authUser, setView])

  const loadConfig = useCallback(async () => {
    try {
      const res = await fetch(`${BASE}/site-config`, { headers: authHeaders(authToken) })
      if (!res.ok) throw new Error(await res.text())
      const data: SiteConfig = await res.json()
      setConfig(data)
      setIntervalVal(data.check_interval_hours)
      setAlertsEnabled(data.alerts_enabled)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load config')
    }
  }, [authToken])

  const loadSubCount = useCallback(async () => {
    try {
      const res = await fetch(`${BASE}/subscribers/count`)
      if (res.ok) setSubCount((await res.json()).count)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => {
    loadConfig()
    loadSubCount()
  }, [loadConfig, loadSubCount])

  const save = async () => {
    setSaving(true)
    setSaveMsg('')
    try {
      const res = await fetch(`${BASE}/site-config`, {
        method: 'PUT',
        headers: authHeaders(authToken),
        body: JSON.stringify({ check_interval_hours: interval, alerts_enabled: alertsEnabled }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setSaveMsg('Settings saved.')
      await loadConfig()
      if (data.next_run) setSaveMsg(`Settings saved. Next check: ${fmtTime(data.next_run)}`)
    } catch (e) {
      setSaveMsg(e instanceof Error ? e.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const runNow = async () => {
    setTriggering(true)
    try {
      await fetch(`${BASE}/site-config/run-now`, {
        method: 'POST',
        headers: authHeaders(authToken),
      })
      setSaveMsg('Flood check triggered — check server logs.')
    } catch {
      setSaveMsg('Failed to trigger check')
    } finally {
      setTriggering(false)
      setTimeout(() => setSaveMsg(''), 5000)
    }
  }

  if (!authUser || authUser.role !== 'admin') return null

  return (
    <div className={styles.page}>
      <div className={styles.hero}>
        <div className={styles.heroInner}>
          <div className={styles.badge}>Admin only</div>
          <h1 className={styles.heroTitle}>Site Configuration</h1>
          <p className={styles.heroSub}>Control automated flood checks and subscriber alert scheduling.</p>
        </div>
      </div>

      <div className={styles.content}>
        {error && <div className={styles.errorBanner}>{error}</div>}

        {/* Status cards */}
        <div className={styles.statsRow}>
          <StatCard label="Active subscribers" value={subCount !== null ? String(subCount) : '…'} accent />
          <StatCard label="Last check" value={fmtTime(config?.last_run ?? null)} />
          <StatCard label="Next check" value={fmtTime(config?.next_run ?? null)} />
          <StatCard label="Alerts" value={config ? (config.alerts_enabled ? 'Enabled' : 'Disabled') : '…'} ok={config?.alerts_enabled} />
        </div>

        {/* Settings panel */}
        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>Flood Check Schedule</h2>
          <p className={styles.panelDesc}>
            At each interval, HydroAI runs one prediction per unique subscriber location.
            If risk is <strong>High</strong>, all subscribers for that location receive an alert email.
          </p>

          <div className={styles.field}>
            <label className={styles.label}>Check frequency</label>
            <div className={styles.intervalGrid}>
              {INTERVALS.map(opt => (
                <button
                  key={opt.value}
                  className={`${styles.intervalBtn} ${interval === opt.value ? styles.intervalActive : ''}`}
                  onClick={() => setIntervalVal(opt.value)}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Automated alerts</label>
            <div className={styles.toggleRow}>
              <button
                className={`${styles.toggle} ${alertsEnabled ? styles.toggleOn : styles.toggleOff}`}
                onClick={() => setAlertsEnabled(v => !v)}
                aria-label="Toggle alerts"
              >
                <span className={styles.toggleThumb} />
              </button>
              <span className={styles.toggleLabel}>
                {alertsEnabled ? 'Enabled — scheduler is running' : 'Disabled — no scheduled checks'}
              </span>
            </div>
          </div>

          <div className={styles.actions}>
            <button className={styles.saveBtn} onClick={save} disabled={saving}>
              {saving ? 'Saving…' : 'Save settings'}
            </button>
            <button className={styles.runBtn} onClick={runNow} disabled={triggering} title="Run a flood check immediately">
              {triggering ? 'Triggering…' : '▶ Run now'}
            </button>
          </div>

          {saveMsg && <div className={styles.saveMsg}>{saveMsg}</div>}
        </div>

        {/* How it works */}
        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>How automated alerts work</h2>
          <ol className={styles.howList}>
            <li>At each scheduled interval, the system fetches all registered users and active subscribers who have a <strong>location</strong> set.</li>
            <li>Locations are deduplicated — if 10 people listed <em>Pune</em>, only <strong>one</strong> prediction runs for Pune.</li>
            <li>Each prediction pulls live ERA5 rainfall and GloFAS discharge data for that location.</li>
            <li>If the XGBoost model outputs <strong>High risk</strong>, a flood alert email is sent to everyone in that location group.</li>
            <li>Low / Medium risk predictions produce no notification — subscribers are only contacted when it matters.</li>
          </ol>
        </div>

        {/* Role info */}
        <div className={styles.panel}>
          <h2 className={styles.panelTitle}>Admin access</h2>
          <p className={styles.panelDesc}>
            You are signed in as <strong>{authUser.name}</strong> ({authUser.email}) with <span className={styles.roleBadge}>admin</span> role.
            Regular users cannot see this page. To promote another user to admin, update their <code>role</code> field in MongoDB to <code>"admin"</code>.
          </p>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value, accent, ok }: { label: string; value: string; accent?: boolean; ok?: boolean }) {
  return (
    <div className={`${styles.statCard} ${accent ? styles.statAccent : ''}`}>
      <div className={styles.statValue} style={ok === false ? { color: 'var(--high-color)' } : ok === true ? { color: 'var(--low-color)' } : undefined}>
        {value}
      </div>
      <div className={styles.statLabel}>{label}</div>
    </div>
  )
}
