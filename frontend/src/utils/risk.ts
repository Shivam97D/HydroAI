import { RiskLevel } from '../api/hydroai'

export const RISK_CONFIG = {
  Low:    { color: 'var(--low-color)',    bg: 'var(--low-bg)',    icon: '◆', bar: '#00E5A0' },
  Medium: { color: 'var(--medium-color)', bg: 'var(--medium-bg)', icon: '▲', bar: '#FFB800' },
  High:   { color: 'var(--high-color)',   bg: 'var(--high-bg)',   icon: '■', bar: '#FF3D5A' },
} as const

export interface DepthClass {
  label: string
  range: string
  max: number       // upper bound in metres (Infinity for the last class)
  color: string
  icon: string
}

// Human-readable flood depth classes matching real-world impact levels.
// Ankle / Knee / Waist / Chest / Life-threatening
export const DEPTH_CLASSES: DepthClass[] = [
  { label: 'Ankle deep',       range: '< 0.25 m',   max: 0.25,     color: '#FFF59D', icon: '〜' },
  { label: 'Knee deep',        range: '0.25–0.5 m', max: 0.50,     color: '#FFB300', icon: '▲' },
  { label: 'Waist deep',       range: '0.5–1.0 m',  max: 1.00,     color: '#FF6D00', icon: '■' },
  { label: 'Chest deep',       range: '1.0–1.8 m',  max: 1.80,     color: '#D32F2F', icon: '◆' },
  { label: 'Life-threatening', range: '> 1.8 m',    max: Infinity, color: '#6A1B9A', icon: '☠' },
]

export const depthToColor = (depth: number): string => {
  const cls = DEPTH_CLASSES.find(c => depth <= c.max)
  return cls ? cls.color : 'transparent'
}

export const depthToLabel = (depth: number): string => {
  const cls = DEPTH_CLASSES.find(c => depth <= c.max)
  return cls ? cls.label : 'Unknown'
}

export const depthToOpacity = (depth: number): number =>
  Math.min(0.85, 0.35 + depth * 0.2)

export const formatScore = (score: number) =>
  (score * 100).toFixed(1) + '%'

export const formatDepth = (depth: number | null): string =>
  depth == null ? '—' : depth.toFixed(2) + ' m'

export const formatRainfall = (mm: number): string =>
  mm.toFixed(1) + ' mm'

export const formatFlow = (m3s: number): string =>
  m3s.toFixed(0) + ' m³/s'

export const formatElevation = (m: number): string =>
  m.toFixed(0) + ' m'
