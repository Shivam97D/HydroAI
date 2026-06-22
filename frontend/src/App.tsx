import React, { useEffect } from 'react'
import Header from './components/Header'
import DashboardPage from './pages/DashboardPage'
import HistoryPage from './components/HistoryPage'
import AboutPage from './components/AboutPage'
import LoginPage from './pages/LoginPage'
import SignupPage from './pages/SignupPage'
import AwarenessPage from './pages/AwarenessPage'
import SiteConfigPage from './pages/SiteConfigPage'
import { useStore } from './store/useStore'
import styles from './App.module.css'

export default function App() {
  const { view, theme } = useStore()

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const isAuthPage = view === 'login' || view === 'signup'

  return (
    <div className={styles.app}>
      {!isAuthPage && <Header />}
      <main className={isAuthPage ? '' : styles.main}>
        {view === 'dashboard' && <DashboardPage />}
        {view === 'history'   && <HistoryPage />}
        {view === 'about'     && <AboutPage />}
        {view === 'awareness'  && <AwarenessPage />}
        {view === 'login'      && <LoginPage />}
        {view === 'signup'     && <SignupPage />}
        {view === 'siteconfig' && <SiteConfigPage />}
      </main>
      {!isAuthPage && <Footer />}
    </div>
  )
}

function Footer() {
  return (
    <footer className={styles.footer}>
      <span>HydroAI © 2025</span>
      <span className={styles.footerSep}>·</span>
      <span>Flood Intelligence Platform</span>
      <span className={styles.footerSep}>·</span>
      <a href="/docs" target="_blank" rel="noopener" className={styles.footerLink}>API Docs</a>
    </footer>
  )
}
