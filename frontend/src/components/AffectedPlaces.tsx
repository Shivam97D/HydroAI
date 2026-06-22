import React from 'react'
import { AffectedPlace } from '../api/hydroai'
import { depthToColor } from '../utils/risk'
import { useStore } from '../store/useStore'
import styles from './AffectedPlaces.module.css'

interface Props {
  places: AffectedPlace[]
  maxDepth: number | null
}

export default function AffectedPlaces({ places, maxDepth }: Props) {
  const { setFocusTarget, setActiveTab, focusTarget } = useStore()
  if (!places.length) return null

  const sorted = [...places].sort((a, b) => b.water_depth - a.water_depth)

  const focusPlace = (place: AffectedPlace) => {
    if (place.lat == null || place.lon == null) return
    setActiveTab('map')                       // switch off the raster tab if active
    setFocusTarget({ lat: place.lat, lon: place.lon, name: place.name })
  }

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.label}>AFFECTED_AREAS</span>
        <div className={styles.stats}>
          <span className={styles.count}>{places.length} ZONES</span>
          {maxDepth != null && (
            <span className={styles.maxDepth}>
              MAX {maxDepth.toFixed(2)} m
            </span>
          )}
        </div>
      </div>

      <div className={styles.list}>
        {sorted.map((place, i) => {
          const pct = maxDepth ? (place.water_depth / maxDepth) * 100 : 50
          const color = depthToColor(place.water_depth)
          const clickable = place.lat != null && place.lon != null
          const isActive = clickable && focusTarget?.name === place.name
          return (
            <button
              type="button"
              key={`${place.name}-${i}`}
              className={`${styles.item} ${clickable ? styles.clickable : ''} ${isActive ? styles.active : ''} animate-fade-in-${Math.min(i + 1, 4)}`}
              onClick={() => focusPlace(place)}
              disabled={!clickable}
              title={clickable ? `Zoom map to ${place.name}` : undefined}
            >
              <div className={styles.itemLeft}>
                <span className={styles.rank}>{String(i + 1).padStart(2, '0')}</span>
                <div className={styles.itemInfo}>
                  <span className={styles.placeName}>{place.name}</span>
                  <div className={styles.depthBar}>
                    <div
                      className={styles.depthFill}
                      style={{ width: `${pct}%`, background: color }}
                    />
                  </div>
                </div>
              </div>
              <div className={styles.itemRight}>
                <span className={styles.depth} style={{ color }}>
                  {place.water_depth.toFixed(2)}
                </span>
                <span className={styles.unit}>m</span>
                {clickable && <span className={styles.locateIcon} aria-hidden>◎</span>}
              </div>
            </button>
          )
        })}
      </div>

      <div className={styles.footer}>
        <span className={styles.footerNote}>
          ◈ Areas with water depth above threshold ({'>'}0.3 m)
        </span>
      </div>
    </div>
  )
}
