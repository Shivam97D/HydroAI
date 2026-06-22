import React from 'react'
import { useStore } from '../store/useStore'
import styles from './ModelAccuracy.module.css'

/**
 * Real model-validation metrics from the held-out test set (served by /metrics).
 * These are the headline accuracy numbers for the report.
 */
export default function ModelAccuracy() {
  const { metrics } = useStore()
  if (!metrics) return null

  const r = metrics.regression_discharge_forecast
  const c = metrics.classification_flood_risk

  const cards = [
    { label: 'NSE', value: r.NSE.toFixed(3), good: r.NSE >= 0.85, note: 'discharge forecast' },
    { label: 'R²', value: r.R2.toFixed(3), good: r.R2 >= 0.8, note: 'observed vs sim' },
    { label: 'ROC-AUC', value: c.ROC_AUC.toFixed(3), good: c.ROC_AUC >= 0.85, note: 'flood classifier' },
    { label: 'FAR', value: `${(c.FAR * 100).toFixed(1)}%`, good: c.FAR <= 0.2, note: 'false-alarm rate' },
  ]

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.label}>MODEL_VALIDATION</span>
        <span className={styles.badge}>held-out test</span>
      </div>

      <div className={styles.grid}>
        {cards.map(card => (
          <div key={card.label} className={styles.card}>
            <div className={styles.cardTop}>
              <span className={styles.metricLabel}>{card.label}</span>
              <span className={`${styles.dot} ${card.good ? styles.ok : styles.warn}`} />
            </div>
            <div className={styles.value}>{card.value}</div>
            <div className={styles.note}>{card.note}</div>
          </div>
        ))}
      </div>

      <div className={styles.source}>
        {metrics.data_source} · {metrics.data_period}
      </div>
    </div>
  )
}
