import React, { Suspense, lazy } from 'react'
import { PredictResponse } from '../api/hydroai'
import { useStore } from '../store/useStore'
import { RandomLoader } from './Loaders'
import styles from './SimulationPanel.module.css'

// Lazy-load the heavy Leaflet map
const FloodMap = lazy(() => import('./FloodMap'))

interface Props { data: PredictResponse }

export default function SimulationPanel({ data }: Props) {
  const { activeTab, setActiveTab } = useStore()

  return (
    <div className={styles.panel}>
      {/* ── Tabs ─────────────────────────────────────────────────── */}
      <div className={styles.tabs}>
        <button
          className={`${styles.tab} ${activeTab === 'map' ? styles.active : ''}`}
          onClick={() => setActiveTab('map')}
        >
          <MapIcon /> Flood Map
        </button>
        {data.flood_map_url && (
          <button
            className={`${styles.tab} ${activeTab === 'image' ? styles.active : ''}`}
            onClick={() => setActiveTab('image')}
          >
            <ImageIcon /> Raster View
          </button>
        )}
        <div className={styles.tabMeta}>
          {data.run_simulation && data.flooded_area_km2 != null && (
            <span className={styles.maxDepthBadge}>
              Area: {data.flooded_area_km2.toFixed(1)} km²
            </span>
          )}
          {data.run_simulation && data.max_water_depth != null && (
            <span className={styles.maxDepthBadge}>
              Max depth: {data.max_water_depth.toFixed(2)} m
            </span>
          )}
          {!data.run_simulation && (
            <span className={styles.terrainBadge}>
              Risk zone · {(data.risk_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>

      {/* ── Map view ─────────────────────────────────────────────── */}
      {activeTab === 'map' && (
        <Suspense fallback={<MapLoader />}>
          <FloodMap data={data} />
        </Suspense>
      )}

      {/* ── Image view ───────────────────────────────────────────── */}
      {activeTab === 'image' && data.flood_map_url && (
        <div className={styles.imageWrap}>
          <img
            src={data.flood_map_url}
            alt="Flood extent map"
            className={styles.floodImage}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none'
            }}
          />
          <a
            href={data.flood_map_url}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.downloadLink}
          >
            ↗ Open full size
          </a>
        </div>
      )}
    </div>
  )
}

function MapLoader() {
  return (
    <div className={styles.loader}>
      <RandomLoader />
      <span>Loading map…</span>
    </div>
  )
}

function MapIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path d="M1 2l3.5 1.5L7.5 2 11 3.5v6.5l-3.5-1.5-3 1.5L1 8.5V2z"
        stroke="currentColor" strokeWidth="1" strokeLinejoin="round" fill="none" />
    </svg>
  )
}

function ImageIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <rect x="1" y="2" width="10" height="8" rx="1" stroke="currentColor" strokeWidth="1" fill="none" />
      <circle cx="4" cy="5" r="1" fill="currentColor" />
      <path d="M1 8l3-2.5 2 2 2-2.5 3 3" stroke="currentColor" strokeWidth="1" strokeLinejoin="round" />
    </svg>
  )
}
