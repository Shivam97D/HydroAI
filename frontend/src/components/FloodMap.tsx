import React, { useEffect, useRef, useState, useMemo } from 'react'
import {
  MapContainer, TileLayer, ImageOverlay, CircleMarker, Popup,
  Polyline, Marker, useMap,
} from 'react-leaflet'
import L from 'leaflet'
import { PredictResponse } from '../api/hydroai'
import { useStore } from '../store/useStore'
import { DEPTH_CLASSES } from '../utils/risk'
import styles from './FloodMap.module.css'

type LayerMode = 'map' | 'satellite'

interface Props { data: PredictResponse }

// Re-centres / fits map when prediction changes
function MapFly({ lat, lon, geojson }: { lat: number; lon: number; geojson: GeoJSON.FeatureCollection | null }) {
  const map = useMap()
  useEffect(() => {
    if (geojson) {
      const flood = {
        ...geojson,
        features: geojson.features.filter(f => !f.properties?.feature_type),
      }
      if (flood.features.length > 0) {
        try {
          const layer = L.geoJSON(flood as any)
          map.fitBounds(layer.getBounds().pad(0.15), { animate: true, duration: 1.0 })
          return
        } catch { /* fall through */ }
      }
    }
    map.flyTo([lat, lon], 12, { duration: 1.2 })
  }, [lat, lon, geojson, map])
  return null
}

// Flies the map to a clicked affected-area; re-fires on every click via nonce.
function FocusFly({ target }: { target: { lat: number; lon: number; nonce: number } | null }) {
  const map = useMap()
  useEffect(() => {
    if (target) map.flyTo([target.lat, target.lon], 15, { duration: 1.0 })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target?.nonce])
  return null
}

// Flow-direction arrow marker using a rotated SVG divIcon.
// angle_deg follows the standard math convention (0° = East, CCW).
// We convert to CSS clockwise-from-north for the visual arrow (↑).
function FlowArrow({ lat, lon, angleDeg, speed }: { lat: number; lon: number; angleDeg: number; speed: number }) {
  const cssAngle = 90 - angleDeg            // math → CSS transform
  const opacity  = Math.max(0.5, Math.min(1, 0.5 + speed * 0.5))
  const icon = useMemo(() => L.divIcon({
    html: `<div style="width:18px;height:18px;transform:rotate(${cssAngle}deg);opacity:${opacity};">
      <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
        <line x1="9" y1="15" x2="9" y2="3" stroke="#00e5ff" stroke-width="2" stroke-linecap="round"/>
        <polyline points="5,7 9,3 13,7" stroke="#00e5ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
      </svg>
    </div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    className: '',
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }), [cssAngle, opacity])

  return <Marker position={[lat, lon]} icon={icon} interactive={false} zIndexOffset={-100} />
}

export default function FloodMap({ data }: Props) {
  const { geojsonData, focusTarget } = useStore()
  const [layerMode, setLayerMode] = useState<LayerMode>('map')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const wrapRef = useRef<HTMLDivElement>(null)

  // Sync fullscreen state with browser API
  useEffect(() => {
    const onChange = () => setIsFullscreen(!!document.fullscreenElement)
    document.addEventListener('fullscreenchange', onChange)
    return () => document.removeEventListener('fullscreenchange', onChange)
  }, [])

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      wrapRef.current?.requestFullscreen().catch(() => {})
    } else {
      document.exitFullscreen().catch(() => {})
    }
  }

  // Extract the river channel line + flow arrows from the GeoJSON
  const { channelCoords, arrowFeatures } = useMemo(() => {
    if (!geojsonData) return { channelCoords: [], arrowFeatures: [] }

    const channelFeat = geojsonData.features.find(f => f.properties?.feature_type === 'river_channel')
    const arrowFeats  = geojsonData.features.filter(f => f.properties?.feature_type === 'flow_arrow')

    const coords: [number, number][] =
      channelFeat?.geometry.type === 'LineString'
        ? (channelFeat.geometry as GeoJSON.LineString).coordinates.map(
            ([lon, lat]) => [lat, lon]          // GeoJSON [lon,lat] → Leaflet [lat,lon]
          )
        : []

    return { channelCoords: coords, arrowFeatures: arrowFeats }
  }, [geojsonData])

  // Leaflet bounds [[south, west], [north, east]] for the depth-raster overlay
  const overlayBounds = useMemo<L.LatLngBoundsExpression | null>(() => {
    const b = data.flood_bounds
    if (!b || b.length !== 4) return null
    return [[b[0], b[1]], [b[2], b[3]]]
  }, [data.flood_bounds])

  // Active flood: ML model said High risk AND we have a depth-class overlay
  const isActiveFlood = data.run_simulation && !!data.flood_overlay_url
  const hasFlood = isActiveFlood && !!overlayBounds

  return (
    <div
      ref={wrapRef}
      className={`${styles.mapWrap} ${isFullscreen ? styles.fullscreen : ''}`}
    >
      {/* ── Layer toggle ─────────────────────────────────────────── */}
      <div className={styles.layerToggle}>
        <button
          className={`${styles.layerBtn} ${layerMode === 'map' ? styles.layerActive : ''}`}
          onClick={() => setLayerMode('map')}
        >
          Map
        </button>
        <button
          className={`${styles.layerBtn} ${layerMode === 'satellite' ? styles.layerActive : ''}`}
          onClick={() => setLayerMode('satellite')}
        >
          Satellite
        </button>
      </div>

      {/* ── Fullscreen button ─────────────────────────────────────── */}
      <button
        className={styles.fullscreenBtn}
        onClick={toggleFullscreen}
        title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
      >
        {isFullscreen
          ? <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor"><path d="M5 1H1v4h2V3h2V1zM9 1v2h2v2h2V1H9zM1 9v4h4v-2H3V9H1zm10 2H9v2h4V9h-2v2z"/></svg>
          : <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor"><path d="M1 1v4h2V3h2V1H1zm8 0v2h2v2h2V1H9zM1 9v4h4v-2H3V9H1zm10 2H9v2h4V9h-2v2z"/></svg>
        }
      </button>

      <MapContainer
        center={[data.latitude, data.longitude]}
        zoom={12}
        className={styles.map}
        zoomControl={true}
        attributionControl={true}
      >
        {/* ── Base tile layers ─────────────────────────────────────── */}
        {layerMode === 'map' && (
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>'
            maxZoom={19}
          />
        )}
        {layerMode === 'satellite' && (
          <>
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution="&copy; Esri, Maxar, GeoEye, USDA, USGS, AeroGRID, IGN"
              maxZoom={18}
            />
            {/* Labels overlay on satellite */}
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}"
              maxZoom={18}
              opacity={0.75}
            />
          </>
        )}

        <MapFly lat={data.latitude} lon={data.longitude} geojson={geojsonData} />
        <FocusFly target={focusTarget} />

        {/* ── Q2 risk zone (always visible, faint steel-blue) ─────── */}
        {data.risk_zone_overlay_url && overlayBounds && (
          <ImageOverlay
            key={data.risk_zone_overlay_url}
            url={data.risk_zone_overlay_url}
            bounds={overlayBounds}
            opacity={1}
            zIndex={395}
          />
        )}

        {/* ── Active flood depth raster (depth classes, only on floods) */}
        {hasFlood && overlayBounds && (
          <ImageOverlay
            key={data.flood_overlay_url!}
            url={data.flood_overlay_url!}
            bounds={overlayBounds}
            opacity={0.88}
            zIndex={400}
          />
        )}

        {/* ── River channel line (glow underlay + bright core) ─────── */}
        {channelCoords.length >= 2 && (
          <>
            <Polyline
              positions={channelCoords}
              pathOptions={{ color: '#00bfff', weight: 9, opacity: 0.3, lineCap: 'round', lineJoin: 'round' }}
            />
            <Polyline
              positions={channelCoords}
              pathOptions={{ color: '#7df9ff', weight: 3, opacity: 0.95, lineCap: 'round', lineJoin: 'round' }}
            />
          </>
        )}

        {/* ── Flow direction arrows ─────────────────────────────────── */}
        {arrowFeatures.map((f, i) => {
          const coords = (f.geometry as GeoJSON.Point).coordinates
          return (
            <FlowArrow
              key={i}
              lat={coords[1]}
              lon={coords[0]}
              angleDeg={f.properties?.angle_deg ?? 0}
              speed={f.properties?.speed ?? 0.5}
            />
          )
        })}

        {/* ── Focused affected-area highlight ──────────────────────── */}
        {focusTarget && (
          <CircleMarker
            key={focusTarget.nonce}
            center={[focusTarget.lat, focusTarget.lon]}
            radius={14}
            pathOptions={{
              color: '#ffffff',
              fillColor: '#00e5ff',
              fillOpacity: 0.35,
              weight: 2,
            }}
          >
            <Popup>
              <div className={styles.popup}>
                <strong>{focusTarget.name}</strong>
                <span>Affected area</span>
              </div>
            </Popup>
          </CircleMarker>
        )}

        {/* ── Query-point marker ───────────────────────────────────── */}
        <CircleMarker
          center={[data.latitude, data.longitude]}
          radius={8}
          pathOptions={{
            color: 'var(--accent)',
            fillColor: 'var(--accent)',
            fillOpacity: 0.9,
            weight: 2,
          }}
        >
          <Popup>
            <div className={styles.popup}>
              <strong>{data.location}</strong>
              <span>Risk: {data.risk_level}</span>
              <span>Score: {(data.risk_score * 100).toFixed(1)}%</span>
              {data.flood_stage_m != null && <span>Stage: {data.flood_stage_m.toFixed(2)} m</span>}
            </div>
          </Popup>
        </CircleMarker>
      </MapContainer>

      {/* ── Legend ───────────────────────────────────────────────────── */}
      <div className={styles.legend}>
        {isActiveFlood && (
          <>
            <div className={styles.legendTitle}>Active Flood Depth</div>
            {DEPTH_CLASSES.map(cls => (
              <div key={cls.label} className={styles.legendItem}>
                <span className={styles.legendSwatch} style={{ background: cls.color }} />
                <span className={styles.legendLabel}>
                  <span className={styles.legendIcon}>{cls.icon}</span>
                  {cls.label}
                </span>
                <span className={styles.legendRange}>{cls.range}</span>
              </div>
            ))}
            <div className={styles.legendDivider} />
          </>
        )}
        <div className={styles.legendItem}>
          <span className={styles.legendSwatch} style={{ background: '#1e88e5', opacity: 0.55 }} />
          <span className={styles.legendLabel}>Q2 risk zone</span>
        </div>
        <div className={styles.legendItem}>
          <span className={styles.legendLine} />
          <span className={styles.legendLabel}>River channel</span>
        </div>
        <div className={styles.legendItem}>
          <span className={styles.legendArrow}>↑</span>
          <span className={styles.legendLabel}>Flow direction</span>
        </div>
        <div className={styles.legendItem}>
          <span className={styles.legendSwatch} style={{ background: 'var(--accent)', borderRadius: '50%' }} />
          <span className={styles.legendLabel}>Query point</span>
        </div>
      </div>

      {/* ── Q2 context badge (only on non-flood days) ───────────────── */}
      {!isActiveFlood && data.risk_zone_overlay_url && (
        <div className={styles.noFloodBadge}>
          Q2 flood risk zone · Area that floods in a 2-yr event · Current risk {(data.risk_score * 100).toFixed(0)}%
        </div>
      )}
    </div>
  )
}
