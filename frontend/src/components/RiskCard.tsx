import React from 'react'
import { PredictResponse } from '../api/hydroai'
import { RISK_CONFIG, formatScore } from '../utils/risk'
import styles from './RiskCard.module.css'

interface Props { data: PredictResponse }

export default function RiskCard({ data }: Props) {
  const cfg = RISK_CONFIG[data.risk_level]
  const pct = data.risk_score * 100

  return (
    <div className={`${styles.card} animate-fade-in`} style={{ '--risk-color': cfg.color } as React.CSSProperties}>
      {/* ── Header ──────────────────────────────────────────────────── */}
      <div className={styles.header}>
        <span className={styles.sectionLabel}>RISK_ASSESSMENT</span>
        <span className={styles.location}>{data.location.toUpperCase()}</span>
      </div>

      {/* ── Score ring ──────────────────────────────────────────────── */}
      <div className={styles.scoreArea}>
        <div className={styles.ringWrap}>
          <svg className={styles.ring} viewBox="0 0 120 120">
            {/* Track */}
            <circle cx="60" cy="60" r="50" className={styles.ringTrack} />
            {/* Progress */}
            <circle
              cx="60" cy="60" r="50"
              className={styles.ringProgress}
              stroke={cfg.color}
              strokeDasharray={`${pct * 3.14159} 314.159`}
              transform="rotate(-90 60 60)"
            />
          </svg>
          <div className={styles.ringInner}>
            <span className={styles.scoreValue}>{(pct).toFixed(0)}</span>
            <span className={styles.scorePct}>%</span>
          </div>
        </div>

        <div className={styles.riskMeta}>
          <div className={styles.levelBadge} style={{ color: cfg.color, background: cfg.bg }}>
            <span className={styles.levelIcon}>{cfg.icon}</span>
            <span className={styles.levelText}>{data.risk_level.toUpperCase()} RISK</span>
          </div>

          <div className={styles.simStatus}>
            <span className={styles.simDot} style={{ background: data.run_simulation ? cfg.color : 'var(--text-dim)' }} />
            <span className={styles.simLabel}>
              SIMULATION: {data.run_simulation ? 'ACTIVE' : 'SKIPPED'}
            </span>
          </div>

          <div className={styles.coords}>
            <CoordRow label="LAT" value={data.latitude.toFixed(4) + '°'} />
            <CoordRow label="LON" value={data.longitude.toFixed(4) + '°'} />
          </div>
        </div>
      </div>

      {/* ── Score bar ───────────────────────────────────────────────── */}
      <div className={styles.barSection}>
        <div className={styles.barTrack}>
          <div
            className={styles.barFill}
            style={{ width: formatScore(data.risk_score), background: cfg.color }}
          />
          {/* Threshold markers */}
          <div className={styles.marker} style={{ left: '30%' }} title="Low threshold" />
          <div className={styles.marker} style={{ left: '60%' }} title="High threshold" />
        </div>
        <div className={styles.barLabels}>
          <span>0</span>
          <span style={{ color: 'var(--low-color)' }}>▸ 0.3</span>
          <span style={{ color: 'var(--medium-color)' }}>▸ 0.6</span>
          <span>1.0</span>
        </div>
      </div>

      {/* ── Insight ─────────────────────────────────────────────────── */}
      <div className={styles.insight}>
        <span className={styles.insightIcon}>◈</span>
        <p className={styles.insightText}>{data.insight}</p>
      </div>
    </div>
  )
}

function CoordRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'baseline' }}>
      <span style={{ fontSize: 9, letterSpacing: '0.12em', color: 'var(--text-muted)', width: 28 }}>{label}</span>
      <span style={{ fontSize: 12, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{value}</span>
    </div>
  )
}
