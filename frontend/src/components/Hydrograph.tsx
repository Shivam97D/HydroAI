import React from 'react'
import { useStore } from '../store/useStore'
import styles from './Hydrograph.module.css'

/**
 * River-discharge hydrograph (real GloFAS data): past reanalysis + forecast,
 * with the reach's return-period danger thresholds overlaid. Pure SVG — no
 * charting dependency.
 */
export default function Hydrograph() {
  const { hydrograph } = useStore()
  if (!hydrograph || !hydrograph.time?.length) return null

  const W = 760, H = 240
  const padL = 52, padR = 16, padT = 16, padB = 28
  const innerW = W - padL - padR
  const innerH = H - padT - padB

  const times = hydrograph.time
  const vals = hydrograph.river_discharge.map(v => (v == null ? 0 : v))
  const th = hydrograph.thresholds || {}

  const maxV = Math.max(...vals, th.Q2 ?? 0, ...Object.values(th)) * 1.1 || 1
  const n = vals.length

  const x = (i: number) => padL + (n <= 1 ? innerW / 2 : (i / (n - 1)) * innerW)
  const y = (v: number) => padT + innerH - (v / maxV) * innerH

  // today = boundary between past and forecast
  const todayStr = new Date().toISOString().slice(0, 10)
  let splitIdx = times.findIndex(t => t >= todayStr)
  if (splitIdx < 0) splitIdx = n - 1

  const linePath = vals.map((v, i) => `${i === 0 ? 'M' : 'L'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ')
  const areaPath = `${linePath} L${x(n - 1).toFixed(1)},${y(0)} L${x(0).toFixed(1)},${y(0)} Z`

  const thresholdLines: { key: string; label: string; color: string }[] = [
    { key: 'warning', label: 'Warning', color: '#FFB300' },
    { key: 'Q2', label: '2-yr', color: '#FF7043' },
    { key: 'Q5', label: '5-yr', color: '#E53935' },
    { key: 'Q25', label: '25-yr', color: '#B71C1C' },
  ]

  const peak = Math.max(...vals)
  const peakIdx = vals.indexOf(peak)

  // sparse x labels
  const tickCount = 6
  const ticks = Array.from({ length: tickCount }, (_, k) => Math.round((k / (tickCount - 1)) * (n - 1)))

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.label}>RIVER_DISCHARGE_HYDROGRAPH</span>
        <span className={styles.badge}>GloFAS · {hydrograph.unit}</span>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className={styles.svg} preserveAspectRatio="xMidYMid meet">
        {/* y gridlines */}
        {[0, 0.25, 0.5, 0.75, 1].map(f => {
          const yy = padT + innerH - f * innerH
          return (
            <g key={f}>
              <line x1={padL} y1={yy} x2={W - padR} y2={yy} stroke="rgba(255,255,255,0.06)" />
              <text x={padL - 8} y={yy + 3} textAnchor="end" className={styles.axisText}>
                {Math.round(f * maxV)}
              </text>
            </g>
          )
        })}

        {/* forecast shading */}
        {splitIdx < n - 1 && (
          <rect x={x(splitIdx)} y={padT} width={x(n - 1) - x(splitIdx)} height={innerH}
                fill="rgba(80,160,255,0.06)" />
        )}

        {/* threshold lines */}
        {thresholdLines.map(t => {
          const v = th[t.key]
          if (v == null || v > maxV) return null
          return (
            <g key={t.key}>
              <line x1={padL} y1={y(v)} x2={W - padR} y2={y(v)}
                    stroke={t.color} strokeWidth={1} strokeDasharray="4 3" opacity={0.7} />
              <text x={W - padR - 2} y={y(v) - 3} textAnchor="end" className={styles.thLabel} fill={t.color}>
                {t.label}
              </text>
            </g>
          )
        })}

        {/* area + line */}
        <defs>
          <linearGradient id="hgFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(80,160,255,0.45)" />
            <stop offset="100%" stopColor="rgba(80,160,255,0.02)" />
          </linearGradient>
        </defs>
        <path d={areaPath} fill="url(#hgFill)" />
        <path d={linePath} fill="none" stroke="#4FA8FF" strokeWidth={1.8} />

        {/* today marker */}
        {splitIdx > 0 && splitIdx < n && (
          <line x1={x(splitIdx)} y1={padT} x2={x(splitIdx)} y2={padT + innerH}
                stroke="rgba(255,255,255,0.35)" strokeWidth={1} strokeDasharray="2 2" />
        )}

        {/* peak dot */}
        {peakIdx >= 0 && (
          <g>
            <circle cx={x(peakIdx)} cy={y(peak)} r={3.5} fill="#fff" stroke="#4FA8FF" strokeWidth={1.5} />
            <text x={x(peakIdx)} y={y(peak) - 8} textAnchor="middle" className={styles.peakText}>
              {peak.toFixed(0)}
            </text>
          </g>
        )}

        {/* x ticks */}
        {ticks.map(i => (
          <text key={i} x={x(i)} y={H - 8} textAnchor="middle" className={styles.axisText}>
            {times[i]?.slice(5)}
          </text>
        ))}
      </svg>

      <div className={styles.footer}>
        <span><i style={{ background: '#4FA8FF' }} /> Discharge</span>
        <span><i style={{ background: 'rgba(80,160,255,0.2)', borderRadius: 0 }} /> Forecast window</span>
        <span className={styles.dim}>Dashed = return-period danger levels</span>
      </div>
    </div>
  )
}
