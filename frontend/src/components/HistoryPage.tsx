import React, { useEffect, useState } from 'react'
import { format, parseISO } from 'date-fns'
import { useStore } from '../store/useStore'
import { api, HistoryRecord } from '../api/hydroai'
import { RISK_CONFIG } from '../utils/risk'
import { RandomLoader } from './Loaders'
import styles from './HistoryPage.module.css'

export default function HistoryPage() {
  const { history, setHistory, historyLoading, setHistoryLoading } = useStore()
  const [locationFilter, setLocationFilter] = useState('')
  const [selected, setSelected] = useState<HistoryRecord | null>(null)

  const load = async (loc?: string) => {
    setHistoryLoading(true)
    try {
      const data = await api.history({ limit: 50, location: loc || undefined })
      setHistory(data)
    } catch (e) {
      setHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleFilter = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') load(locationFilter)
  }

  return (
    <div className={styles.page}>
      {/* ── Header row ──────────────────────────────────────────── */}
      <div className={styles.topBar}>
        <div className={styles.titleGroup}>
          <h2 className={styles.title}>Prediction History</h2>
          <span className={styles.count}>{history.length} records</span>
        </div>

        <div className={styles.filterRow}>
          <input
            className={styles.filterInput}
            placeholder="Filter by location…"
            value={locationFilter}
            onChange={e => setLocationFilter(e.target.value)}
            onKeyDown={handleFilter}
          />
          <button className={styles.filterBtn} onClick={() => load(locationFilter)}>
            Search
          </button>
          {locationFilter && (
            <button className={styles.clearBtn} onClick={() => { setLocationFilter(''); load() }}>
              CLEAR
            </button>
          )}
        </div>
      </div>

      {historyLoading && (
        <div className={styles.loadingRow}>
          <RandomLoader />
          <span>Fetching records…</span>
        </div>
      )}

      {!historyLoading && !history.length && (
        <div className={styles.empty}>
          <span className={styles.emptyIcon}>◇</span>
          <span>No prediction records found</span>
        </div>
      )}

      {/* ── Table ───────────────────────────────────────────────── */}
      {history.length > 0 && (
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Timestamp</th>
                <th>Location</th>
                <th>Risk Level</th>
                <th>Score</th>
                <th>Sim</th>
                <th>Max Depth</th>
                <th>Zones</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {history.map(rec => {
                const cfg = RISK_CONFIG[rec.risk_level]
                return (
                  <tr
                    key={rec.id}
                    className={`${styles.row} ${selected?.id === rec.id ? styles.selected : ''}`}
                    onClick={() => setSelected(selected?.id === rec.id ? null : rec)}
                  >
                    <td className={styles.cellId}>#{rec.id}</td>
                    <td className={styles.cellTime}>
                      {format(parseISO(rec.timestamp), 'MMM d, HH:mm')}
                    </td>
                    <td className={styles.cellLocation}>{rec.location}</td>
                    <td>
                      <span className={styles.riskBadge} style={{ color: cfg.color, background: cfg.bg }}>
                        {rec.risk_level.toUpperCase()}
                      </span>
                    </td>
                    <td className={styles.cellScore}>
                      {(rec.risk_score * 100).toFixed(1)}%
                    </td>
                    <td>
                      <span className={styles.simDot} style={{ background: rec.simulation_run ? 'var(--low-color)' : 'var(--text-dim)' }} />
                    </td>
                    <td className={styles.cellDepth}>
                      {rec.max_water_depth != null ? rec.max_water_depth.toFixed(2) + ' m' : '—'}
                    </td>
                    <td className={styles.cellZones}>{rec.affected_places.length}</td>
                    <td>
                      {rec.flood_map_url && (
                        <a href={rec.flood_map_url} target="_blank" rel="noopener" className={styles.mapLink}>↗</a>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Expanded detail panel ────────────────────────────────── */}
      {selected && (
        <div className={styles.detail}>
          <div className={styles.detailHeader}>
            <span className={styles.detailTitle}>RECORD #{selected.id} — {selected.location.toUpperCase()}</span>
            <button className={styles.detailClose} onClick={() => setSelected(null)}>✕</button>
          </div>
          {selected.insight && (
            <p className={styles.detailInsight}>{selected.insight}</p>
          )}
          {selected.affected_places.length > 0 && (
            <div className={styles.detailPlaces}>
              {selected.affected_places.map((p, i) => (
                <span key={i} className={styles.placeChip}>
                  {p.name} <span style={{ color: 'var(--high-color)' }}>{p.water_depth.toFixed(1)}m</span>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
