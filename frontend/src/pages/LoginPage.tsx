import React, { useState, useEffect } from 'react'
import { useStore } from '../store/useStore'
import { authApi } from '../api/authApi'
import styles from './LoginPage.module.css'

export default function LoginPage() {
  const { setView, setAuthUser, setAuthToken } = useStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
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
    setLoading(true)
    try {
      const res = await authApi.login(email, password)
      setAuthToken(res.token)
      setAuthUser(res.user)
      setView('dashboard')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed')
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
            <h1 className={styles.title}>Welcome back</h1>
            <p className={styles.subtitle}>Sign in to your HydroAI account</p>
          </div>

          <form onSubmit={submit} className={styles.form}>
            {error && <div className={styles.errorMsg}>{error}</div>}
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
              <label className={styles.label}>Password</label>
              <input
                className={styles.input}
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className={styles.submitBtn} disabled={loading}>
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className={styles.switchLink}>
            Don&apos;t have an account?{' '}
            <button onClick={() => setView('signup')} className={styles.linkBtn}>Create one</button>
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
