import React from 'react'
import { FeatureInputs } from '../api/hydroai'
import { formatRainfall, formatFlow, formatElevation } from '../utils/risk'
import styles from './MetricsPanel.module.css'

interface Props { features: FeatureInputs }

export default function MetricsPanel({ features }: Props) {
  const metrics = [
    {
      label: 'RAINFALL_24H',
      value: formatRainfall(features.rainfall_24h),
      raw: features.rainfall_24h,
      max: 200,
      unit: 'mm',
      icon: '🌧',
      warn: features.rainfall_24h > 50,
    },
    {
      label: 'RAINFALL_3D',
      value: formatRainfall(features.rainfall_3d),
      raw: features.rainfall_3d,
      max: 500,
      unit: 'mm',
      icon: '📆',
      warn: features.rainfall_3d > 120,
    },
    {
      label: 'RAINFALL_7D',
      value: formatRainfall(features.rainfall_7d),
      raw: features.rainfall_7d,
      max: 800,
      unit: 'mm',
      icon: '📊',
      warn: features.rainfall_7d > 250,
    },
    {
      label: 'ELEVATION',
      value: formatElevation(features.elevation),
      raw: features.elevation,
      max: 300,
      unit: 'm',
      icon: '⛰',
      warn: features.elevation < 20,
      invertWarn: true,
    },
    {
      label: 'RIVER_FLOW',
      value: formatFlow(features.river_flow),
      raw: features.river_flow,
      max: 2000,
      unit: 'm³/s',
      icon: '🌊',
      warn: features.river_flow > 400,
    },
  ]

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.label}>ENVIRONMENTAL_FEATURES</span>
        <span className={styles.badge}>XGB_INPUT</span>
      </div>

      <div className={styles.grid}>
        {metrics.map((m, i) => (
          <div
            key={m.label}
            className={`${styles.metric} animate-fade-in-${Math.min(i + 1, 4)}`}
          >
            <div className={styles.metricHeader}>
              <span className={styles.metricLabel}>{m.label}</span>
              {m.warn && <span className={styles.warnDot} />}
            </div>
            <div className={styles.metricValue}>{m.value}</div>
            <div className={styles.metricBar}>
              <div
                className={styles.metricBarFill}
                style={{
                  width: `${Math.min((m.raw / m.max) * 100, 100)}%`,
                  background: m.warn ? 'var(--medium-color)' : 'var(--accent)',
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
