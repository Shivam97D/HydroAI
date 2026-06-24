import React, { useState, useEffect } from 'react'
import { useStore } from '../store/useStore'
import { authApi } from '../api/authApi'
import styles from './SignupPage.module.css'

export default function SignupPage() {
  const { setView, setAuthUser, setAuthToken } = useStore()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [location, setLocation] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handler = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    setLoading(true)
    try {
      const res = await authApi.register(name, email, password, location)
      setAuthToken(res.token)
      setAuthUser(res.user)
      setView('dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.page}>
      <div className={styles.layer1} style={{ transform: `translateY(${scrollY * 0.15}px)` }} />
      <div className={styles.layer2} style={{ transform: `translateY(${scrollY * 0.30}px)` }} />
      <div className={styles.layer3} style={{ transform: `translateY(${scrollY * 0.50}px)` }} />

      <div className={styles.content}>
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <div className={styles.logo}><WaveIcon /></div>
            <h1 className={styles.title}>Create your account</h1>
            <p className={styles.subtitle}>Join HydroAI for flood intelligence & alerts</p>
          </div>

          <form onSubmit={submit} className={styles.form}>
            {error && <div className={styles.errorMsg}>{error}</div>}
            <div className={styles.field}>
              <label className={styles.label}>Full name</label>
              <input
                className={styles.input}
                type="text"
                placeholder="Ravi Kumar"
                value={name}
                onChange={e => setName(e.target.value)}
                required
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>Email</label>
              <input
                className={styles.input}
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <div className={styles.field}>
              <label className={styles.label}>City / Area for flood alerts</label>
              <input
                className={styles.input}
                type="text"
                placeholder="e.g. Pune, Mumbai, Nashik"
                value={location}
                onChange={e => setLocation(e.target.value)}
                required
              />
            </div>
            <div className={styles.fieldRow}>
              <div className={styles.field}>
                <label className={styles.label}>Password</label>
                <input
                  className={styles.input}
                  type="password"
                  placeholder="Min. 8 chars"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                />
              </div>
              <div className={styles.field}>
                <label className={styles.label}>Confirm</label>
                <input
                  className={styles.input}
                  type="password"
                  placeholder="Repeat password"
                  value={confirm}
                  onChange={e => setConfirm(e.target.value)}
                  required
                />
              </div>
            </div>
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className={styles.switchLink}>
            Already have an account?{' '}
            <button onClick={() => setView('login')} className={styles.linkBtn}>Sign in</button>
          </p>

          <p className={styles.switchLink} style={{ marginTop: 8 }}>
            <button onClick={() => setView('dashboard')} className={styles.linkBtn}>
              ← Back to app
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}

function WaveIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
      <path d="M2 18 Q5 10 8 18 Q11 26 14 18 Q17 10 20 18 Q23 26 26 18" stroke="white" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
      <path d="M2 13 Q5 5 8 13 Q11 21 14 13 Q17 5 20 13 Q23 21 26 13" stroke="rgba(255,255,255,0.45)" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
    </svg>
  )
}
