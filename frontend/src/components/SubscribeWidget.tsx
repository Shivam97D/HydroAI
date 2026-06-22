import React, { useState } from 'react'
import { authApi } from '../api/authApi'
import styles from './SubscribeWidget.module.css'

interface Props {
  dark?: boolean
}

export default function SubscribeWidget({ dark = false }: Props) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [location, setLocation] = useState('')
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [msg, setMsg] = useState('')

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setStatus('loading')
    try {
      const res = await authApi.subscribe(name, email, location)
      setStatus('success')
      setMsg(res.message)
      setName('')
      setEmail('')
    } catch (err: unknown) {
      setStatus('error')
      setMsg(err instanceof Error ? err.message : 'Subscription failed')
    }
  }

  if (status === 'success') {
    return (
      <div className={`${styles.success} ${dark ? styles.dark : ''}`}>
        <span className={styles.successIcon}>✓</span>
        <div>
          <strong>You&apos;re subscribed!</strong>
          <p>{msg}. Check your inbox for a welcome email.</p>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={submit} className={`${styles.widget} ${dark ? styles.dark : ''}`}>
      <div className={styles.fields}>
        <input
          className={styles.input}
          type="text"
          placeholder="Your name"
          value={name}
          onChange={e => setName(e.target.value)}
          required
        />
        <input
          className={styles.input}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          className={styles.input}
          type="text"
          placeholder="Your city (e.g. Pune)"
          value={location}
          onChange={e => setLocation(e.target.value)}
          required
        />
        <button type="submit" className={styles.btn} disabled={status === 'loading'}>
          {status === 'loading' ? 'Subscribing…' : 'Get Alerts'}
        </button>
      </div>
      {status === 'error' && <p className={styles.errorText}>{msg}</p>}
      <p className={styles.note}>Free. Instant alerts for high-risk flood events. Unsubscribe anytime.</p>
    </form>
  )
}
