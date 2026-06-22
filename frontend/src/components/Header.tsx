import React, { useEffect, useState } from 'react'
import { useStore, AppView } from '../store/useStore'
import { api } from '../api/hydroai'
import SubscribeWidget from './SubscribeWidget'
import styles from './Header.module.css'

const NAV_ITEMS: { id: AppView; label: string; adminOnly?: boolean }[] = [
  { id: 'dashboard',  label: 'Forecast'   },
  { id: 'history',    label: 'History'    },
  { id: 'awareness',  label: 'Awareness'  },
  { id: 'about',      label: 'About'      },
  { id: 'siteconfig', label: 'Site Config', adminOnly: true },
]

export default function Header() {
  const { view, setView, health, setHealth, theme, setTheme, authUser, logout } = useStore()
  const [showSubscribe, setShowSubscribe] = useState(false)

  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth(null))
  }, [setHealth])

  return (
    <header className={styles.header}>
      {/* Left – brand */}
      <div className={styles.brand}>
        <div className={styles.logoMark}>
          <WaveIcon />
        </div>
        <div className={styles.wordmark}>
          <span className={styles.brandName}>HydroAI</span>
          <span className={styles.tagline}>Flood Intelligence</span>
        </div>
      </div>

      {/* Centre – nav */}
      <nav className={styles.nav}>
        {NAV_ITEMS.filter(item => !item.adminOnly || authUser?.role === 'admin').map(item => (
          <button
            key={item.id}
            className={`${styles.navItem} ${view === item.id ? styles.active : ''} ${item.adminOnly ? styles.adminNav : ''}`}
            onClick={() => setView(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {/* Right – controls */}
      <div className={styles.right}>
        {/* Bell icon – subscribe dropdown */}
        <div style={{ position: 'relative' }}>
          <button
            className={styles.alertBtn}
            onClick={() => setShowSubscribe(s => !s)}
            title="Subscribe to flood alerts"
            aria-label="Flood alert subscription"
          >
            <BellIcon />
          </button>
          {showSubscribe && (
            <div className={styles.subscribeDropdown}>
              <div className={styles.subscribeDropdownTitle}>🔔 Flood Alert Subscription</div>
              <SubscribeWidget />
            </div>
          )}
        </div>

        {/* Theme toggle */}
        <button
          className={styles.themeToggle}
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          aria-label="Toggle theme"
        >
          {theme === 'light' ? <MoonIcon /> : <SunIcon />}
        </button>

        {/* Auth */}
        {authUser ? (
          <div className={styles.userMenu}>
            <div className={styles.avatar}>{authUser.name[0].toUpperCase()}</div>
            <span className={styles.userName}>{authUser.name.split(' ')[0]}</span>
            <button className={styles.logoutBtn} onClick={logout}>Sign out</button>
          </div>
        ) : (
          <div className={styles.authBtns}>
            <button className={styles.signInBtn} onClick={() => setView('login')}>Sign in</button>
            <button className={styles.signUpBtn} onClick={() => setView('signup')}>Sign up</button>
          </div>
        )}

        {/* Status */}
        <div className={styles.status}>
          <div className={`${styles.dot} ${health?.status === 'ok' ? styles.online : styles.offline}`} />
          <span className={styles.statusLabel}>
            {health ? (health.status === 'ok' ? 'Online' : 'Degraded') : 'Connecting'}
          </span>
        </div>
      </div>
    </header>
  )
}

function WaveIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
      <path
        d="M2 14 Q5 7 8 14 Q11 21 14 14 Q17 7 20 14"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        fill="none"
      />
      <path
        d="M2 9 Q5 2 8 9 Q11 16 14 9 Q17 2 20 9"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        fill="none"
        opacity="0.45"
      />
    </svg>
  )
}

function BellIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
    </svg>
  )
}

function SunIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/>
      <line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
      <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/>
      <line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
      <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  )
}

function MoonIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  )
}
