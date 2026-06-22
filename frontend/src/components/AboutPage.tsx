import React from 'react'
import styles from './AboutPage.module.css'

const PIPELINE = [
  {
    step: '01',
    title: 'GEOCODING',
    desc: 'Location name resolved to coordinates via OpenStreetMap Nominatim',
    tech: 'Nominatim API',
  },
  {
    step: '02',
    title: 'FEATURE FETCH',
    desc: 'Concurrent fetch of rainfall (OpenWeather), elevation (Open-Elevation), and river-flow data',
    tech: 'OpenWeather · Open-Elevation',
  },
  {
    step: '03',
    title: 'ML INFERENCE',
    desc: 'Pre-trained XGBoost model evaluates 5 environmental features to produce a flood risk score',
    tech: 'XGBoost · scikit-learn',
  },
  {
    step: '04',
    title: 'DECISION GATE',
    desc: 'Risk score gates the simulation: score ≥ 0.6 triggers ANUGA; score ≥ 0.8 amplifies inputs by ×1.3 / ×1.2',
    tech: 'Threshold logic',
  },
  {
    step: '05',
    title: 'ANUGA SIMULATION',
    desc: 'Full 2D shallow-water hydraulic simulation produces water-depth grid over a 0.2° bounding box',
    tech: 'ANUGA · NumPy',
  },
  {
    step: '06',
    title: 'OUTPUT GENERATION',
    desc: 'Flood extent exported as GeoJSON + PNG raster. Affected localities extracted via reverse geocoding',
    tech: 'Matplotlib · Nominatim',
  },
]

export default function AboutPage() {
  return (
    <div className={styles.page}>
      {/* ── Hero ───────────────────────────────────────────────── */}
      <div className={styles.hero}>
        <div className={styles.heroLabel}>SYSTEM_OVERVIEW</div>
        <h1 className={styles.heroTitle}>HydroAI</h1>
        <p className={styles.heroDesc}>
          A hybrid flood-intelligence platform combining machine-learning risk prediction
          with physics-based hydraulic simulation to deliver real-time, spatially-accurate
          flood awareness at any location on Earth.
        </p>
      </div>

      {/* ── Pipeline ───────────────────────────────────────────── */}
      <div className={styles.section}>
        <div className={styles.sectionLabel}>PROCESSING_PIPELINE</div>
        <div className={styles.pipeline}>
          {PIPELINE.map((item, i) => (
            <div key={item.step} className={`${styles.pipeItem} animate-fade-in-${Math.min(i + 1, 4)}`}>
              <div className={styles.pipeStep}>{item.step}</div>
              <div className={styles.pipeContent}>
                <div className={styles.pipeTitle}>{item.title}</div>
                <div className={styles.pipeDesc}>{item.desc}</div>
                <div className={styles.pipeTech}>{item.tech}</div>
              </div>
              {i < PIPELINE.length - 1 && <div className={styles.pipeConnector} />}
            </div>
          ))}
        </div>
      </div>

      {/* ── Risk thresholds ─────────────────────────────────────── */}
      <div className={styles.section}>
        <div className={styles.sectionLabel}>RISK_THRESHOLDS</div>
        <div className={styles.thresholds}>
          {[
            { range: '0 – 30%',   label: 'LOW',    color: 'var(--low-color)',    desc: 'Normal conditions. No simulation triggered.' },
            { range: '30 – 60%',  label: 'MEDIUM', color: 'var(--medium-color)', desc: 'Elevated risk. Monitor conditions. No simulation.' },
            { range: '60 – 80%',  label: 'HIGH',   color: 'var(--high-color)',   desc: 'ANUGA simulation activated. Flood maps generated.' },
            { range: '80 – 100%', label: 'SEVERE', color: 'var(--high-color)',   desc: 'Simulation with amplified inputs (×1.3 rain, ×1.2 flow).' },
          ].map(t => (
            <div key={t.label} className={styles.thresholdRow}>
              <span className={styles.thresholdRange} style={{ color: t.color }}>{t.range}</span>
              <span className={styles.thresholdBadge} style={{ color: t.color, borderColor: t.color }}>{t.label}</span>
              <span className={styles.thresholdDesc}>{t.desc}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Tech stack ─────────────────────────────────────────── */}
      <div className={styles.section}>
        <div className={styles.sectionLabel}>TECH_STACK</div>
        <div className={styles.techGrid}>
          {[
            ['FastAPI', 'REST API framework'],
            ['XGBoost', 'Flood risk ML model'],
            ['ANUGA', 'Hydraulic simulation'],
            ['PostgreSQL', 'Prediction persistence'],
            ['React 18', 'Frontend framework'],
            ['Leaflet', 'Interactive mapping'],
            ['OpenWeather', 'Live rainfall data'],
            ['Nominatim', 'Geocoding & reverse geocoding'],
          ].map(([name, desc]) => (
            <div key={name} className={styles.techCard}>
              <span className={styles.techName}>{name}</span>
              <span className={styles.techDesc}>{desc}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
