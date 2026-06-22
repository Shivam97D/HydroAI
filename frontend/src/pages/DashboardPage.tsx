import React, { useEffect } from 'react'
import SearchBar from '../components/SearchBar'
import RiskCard from '../components/RiskCard'
import MetricsPanel from '../components/MetricsPanel'
import SimulationPanel from '../components/SimulationPanel'
import AffectedPlaces from '../components/AffectedPlaces'
import Hydrograph from '../components/Hydrograph'
import ModelAccuracy from '../components/ModelAccuracy'
import { useStore } from '../store/useStore'
import { api } from '../api/hydroai'
import { runPrediction } from '../lib/runPrediction'
import { RandomLoader } from '../components/Loaders'
import styles from './DashboardPage.module.css'

export default function DashboardPage() {
  const { prediction, loading, error, metrics, setMetrics } = useStore()

  // Load the real model-validation metrics once
  useEffect(() => {
    if (!metrics) api.metrics().then(setMetrics).catch(() => {})
  }, [metrics, setMetrics])

  // Deep-link support: ?location=Pune&date=2019-08-05 auto-runs a prediction
  useEffect(() => {
    const p = new URLSearchParams(window.location.search)
    const loc = p.get('location')
    if (loc) runPrediction(loc, p.get('date') ?? undefined)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className={styles.page}>
      {/* ── Search bar (full width) ──────────────────────────────── */}
      <div className={styles.searchSection}>
        <SearchBar />
      </div>

      {/* ── Scan-line animation while loading ─────────────────────── */}
      {loading && <LoadingOverlay />}

      {/* ── Error ─────────────────────────────────────────────────── */}
      {error && !loading && <ErrorBanner message={error} />}

      {/* ── Welcome state ─────────────────────────────────────────── */}
      {!prediction && !loading && !error && <WelcomeState />}

      {/* ── Results layout ────────────────────────────────────────── */}
      {prediction && !loading && (
        <div className={styles.results}>
          {/* Left column */}
          <div className={styles.colLeft}>
            <RiskCard data={prediction} />
            <MetricsPanel features={prediction.features} />
            <ModelAccuracy />
          </div>

          {/* Centre column (map / simulation) */}
          <div className={styles.colCentre}>
            <SimulationPanel data={prediction} />
            <Hydrograph />
          </div>

          {/* Right column */}
          <div className={styles.colRight}>
            {prediction.affected_places.length > 0 ? (
              <AffectedPlaces
                places={prediction.affected_places}
                maxDepth={prediction.max_water_depth}
              />
            ) : (
              <NoAffectedPlaces ran={prediction.run_simulation} />
            )}
            <LinksPanel data={prediction} />
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Sub-components ──────────────────────────────────────────────────────── */

function LoadingOverlay() {
  return (
    <div className={styles.loading}>
      <div className={styles.loadingInner}>
        <RandomLoader />
        <div className={styles.loadingText}>
          <span className={styles.loadingTitle}>Analysing</span>
          <span className={styles.loadingStep}>Fetching environmental data…</span>
        </div>
      </div>
    </div>
  )
}

function ErrorBanner({ message }: { message: string }) {
  const { setError } = useStore()
  return (
    <div className={styles.error}>
      <span className={styles.errorIcon}>⚠</span>
      <span className={styles.errorMsg}>{message}</span>
      <button className={styles.errorClose} onClick={() => setError(null)}>✕</button>
    </div>
  )
}

function WelcomeState() {
  return (
    <div className={styles.welcome}>
      <div className={styles.welcomeGrid}>
        {/* Animated wave graphic */}
        <div className={styles.welcomeArt}>
          <svg viewBox="0 0 400 200" className={styles.wave}>
            {[0, 1, 2, 3].map(i => (
              <path
                key={i}
                d={`M0 ${100 + i * 18} Q50 ${80 + i * 18} 100 ${100 + i * 18} Q150 ${120 + i * 18} 200 ${100 + i * 18} Q250 ${80 + i * 18} 300 ${100 + i * 18} Q350 ${120 + i * 18} 400 ${100 + i * 18}`}
                stroke="var(--accent)"
                strokeWidth={1.5 - i * 0.3}
                fill="none"
                opacity={0.8 - i * 0.18}
                style={{ animationDelay: `${i * 0.3}s` }}
                className={styles.wavePath}
              />
            ))}
          </svg>
        </div>

        <div className={styles.welcomeText}>
          <h2 className={styles.welcomeTitle}>Enter a location</h2>
          <p className={styles.welcomeDesc}>
            Type any city above for a live flood-risk forecast from real rainfall
            (ERA5) and river discharge (GloFAS), or hit “Replay Real Event” to
            reconstruct a documented past flood. High risk triggers a real-terrain
            inundation simulation on the Copernicus DEM.
          </p>
          <div className={styles.welcomeStats}>
            <Stat label="Rainfall" value="ERA5" />
            <Stat label="Discharge" value="GloFAS" />
            <Stat label="Terrain" value="DEM+HAND" />
            <Stat label="Forecast NSE" value="0.87" />
          </div>
        </div>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statValue}>{value}</span>
      <span className={styles.statLabel}>{label}</span>
    </div>
  )
}

function NoAffectedPlaces({ ran }: { ran: boolean }) {
  return (
    <div className={styles.noPlaces}>
      <span className={styles.noPlacesIcon}>◇</span>
      <span className={styles.noPlacesText}>
        {ran ? 'No areas above depth threshold' : 'Simulation not run'}
      </span>
    </div>
  )
}

function LinksPanel({ data }: { data: import('../api/hydroai').PredictResponse }) {
  if (!data.geojson_url && !data.flood_map_url) return null

  return (
    <div className={styles.links}>
      <div className={styles.linksLabel}>Simulation Outputs</div>
      {data.geojson_url && (
        <a href={data.geojson_url} target="_blank" rel="noopener" className={styles.linkItem}>
          <span className={styles.linkIcon}>{ '{}'}</span>
          <span>flood_extent.geojson</span>
          <span className={styles.linkArrow}>↗</span>
        </a>
      )}
      {data.flood_map_url && (
        <a href={data.flood_map_url} target="_blank" rel="noopener" className={styles.linkItem}>
          <span className={styles.linkIcon}>⬛</span>
          <span>flood_map.png</span>
          <span className={styles.linkArrow}>↗</span>
        </a>
      )}
    </div>
  )
}
