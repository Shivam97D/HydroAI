import React, { useState, useRef } from 'react'
import { useStore } from '../store/useStore'
import { runPrediction } from '../lib/runPrediction'
import { RandomLoaderSmall } from './Loaders'
import styles from './SearchBar.module.css'

const PRESETS = ['Pune', 'Mumbai', 'Sangli', 'Kolhapur', 'Nashik', 'Chennai']

// Documented real flood events (the backend replays that day's real data)
const EVENTS = [
  { label: 'Pune flood · Aug 2019', location: 'Pune', date: '2019-08-05' },
  { label: 'Sangli–Kolhapur · Aug 2019', location: 'Sangli', date: '2019-08-07' },
  { label: 'Pune flood · Sep 2019', location: 'Pune', date: '2019-09-25' },
]

export default function SearchBar() {
  const [query, setQuery] = useState('')
  const [mode, setMode] = useState<'live' | 'historical'>('live')
  const [date, setDate] = useState('2019-08-05')
  const [showPresets, setShowPresets] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const { loading } = useStore()

  const submit = (loc: string, overrideDate?: string) => {
    if (!loc.trim() || loading) return
    setShowPresets(false)
    const useDate = overrideDate ?? (mode === 'historical' ? date : undefined)
    runPrediction(loc, useDate)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') submit(query)
    if (e.key === 'Escape') setShowPresets(false)
  }

  return (
    <div className={styles.wrapper}>
      <div className={styles.label}>
        <span className={styles.labelPrefix}>{'>'}</span>
        Enter a location to analyse
      </div>

      {/* ── Mode toggle: live vs historical replay ───────────────────── */}
      <div className={styles.modeRow}>
        <button
          className={`${styles.modeBtn} ${mode === 'live' ? styles.modeActive : ''}`}
          onClick={() => setMode('live')}
        >● Live forecast</button>
        <button
          className={`${styles.modeBtn} ${mode === 'historical' ? styles.modeActive : ''}`}
          onClick={() => setMode('historical')}
        >⟲ Historical replay</button>
        {mode === 'historical' && (
          <input
            type="date"
            className={styles.dateInput}
            value={date}
            min="1984-01-01"
            max="2024-12-31"
            onChange={e => setDate(e.target.value)}
          />
        )}
      </div>

      <div className={styles.inputRow}>
        <div className={styles.inputWrap}>
          <span className={styles.searchIcon}><CoordIcon /></span>
          <input
            ref={inputRef}
            className={styles.input}
            type="text"
            placeholder="Enter city or coordinates…"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowPresets(true)}
            onBlur={() => setTimeout(() => setShowPresets(false), 200)}
            disabled={loading}
            autoComplete="off"
          />
          {query && (
            <button
              className={styles.clearBtn}
              onClick={() => { setQuery(''); inputRef.current?.focus() }}
            >×</button>
          )}
        </div>

        <button
          className={styles.submitBtn}
          onClick={() => submit(query)}
          disabled={!query.trim() || loading}
        >
          {loading ? <RandomLoaderSmall /> : (<><span>Analyse</span><ArrowIcon /></>)}
        </button>
      </div>

      {/* ── Documented-event quick-launch ────────────────────────────── */}
      <div className={styles.events}>
        <span className={styles.presetsLabel}>Replay real event</span>
        {EVENTS.map(ev => (
          <button
            key={ev.label}
            className={styles.eventChip}
            disabled={loading}
            onClick={() => { setMode('historical'); setDate(ev.date); setQuery(ev.location); submit(ev.location, ev.date) }}
          >
            {ev.label}
          </button>
        ))}
      </div>

      {showPresets && (
        <div className={styles.presets}>
          <span className={styles.presetsLabel}>Quick select</span>
          {PRESETS.map(city => (
            <button
              key={city}
              className={styles.chip}
              onMouseDown={() => { setQuery(city); submit(city) }}
            >
              {city}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function CoordIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.5"/>
      <line x1="8" y1="1" x2="8" y2="5"  stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="8" y1="11" x2="8" y2="15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="1" y1="8" x2="5" y2="8"  stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
      <line x1="11" y1="8" x2="15" y2="8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    </svg>
  )
}

function ArrowIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M2 7h10M8 3l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}
