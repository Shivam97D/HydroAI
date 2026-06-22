// ── Types ─────────────────────────────────────────────────────────────────

export interface AffectedPlace {
  name: string
  water_depth: number
  lat: number | null
  lon: number | null
}

export interface FeatureInputs {
  rainfall_24h: number
  rainfall_3d: number
  rainfall_7d: number
  elevation: number
  river_flow: number
}

export type RiskLevel = 'Low' | 'Medium' | 'High'

export interface PredictResponse {
  location: string
  latitude: number
  longitude: number
  risk_score: number
  risk_level: RiskLevel
  run_simulation: boolean
  flood_map_url: string | null
  geojson_url: string | null
  max_water_depth: number | null
  flooded_area_km2: number | null
  flood_stage_m: number | null
  flood_overlay_url: string | null
  flood_bounds: number[] | null   // [south, west, north, east]
  risk_zone_overlay_url: string | null
  affected_places: AffectedPlace[]
  insight: string
  query_date: string | null
  features: FeatureInputs
}

export interface Hydrograph {
  latitude: number
  longitude: number
  unit: string
  time: string[]
  river_discharge: (number | null)[]
  thresholds: Record<string, number>
}

export interface ModelMetrics {
  study_area: string
  data_period: string
  data_source: string
  regression_discharge_forecast: { NSE: number; RMSE_m3s: number; R2: number; test_samples: number }
  classification_flood_risk: {
    ROC_AUC: number; precision: number; recall: number; FAR: number
    test_samples: number; flood_days_in_test: number
  }
  thresholds_m3s: Record<string, number>
}

export interface HistoryRecord {
  id: number
  location: string
  latitude: number | null
  longitude: number | null
  timestamp: string
  risk_score: number
  risk_level: RiskLevel
  simulation_run: boolean
  flood_map_url: string | null
  geojson_url: string | null
  max_water_depth: number | null
  affected_places: AffectedPlace[]
  insight: string | null
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
  database: string
  version: string
}

// ── Client ────────────────────────────────────────────────────────────────

const BASE = import.meta.env.VITE_API_URL ?? ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  predict: (body: { location?: string; lat?: number; lon?: number; date?: string }) =>
    request<PredictResponse>('/predict', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  hydrograph: (params: { location?: string; lat?: number; lon?: number; past_days?: number; forecast_days?: number }) => {
    const q = new URLSearchParams()
    if (params.location) q.set('location', params.location)
    if (params.lat != null) q.set('lat', String(params.lat))
    if (params.lon != null) q.set('lon', String(params.lon))
    q.set('past_days', String(params.past_days ?? 45))
    q.set('forecast_days', String(params.forecast_days ?? 14))
    return request<Hydrograph>(`/hydrograph?${q}`)
  },

  metrics: () => request<ModelMetrics>('/metrics'),

  health: () => request<HealthResponse>('/health'),

  history: (params?: { limit?: number; offset?: number; location?: string }) => {
    const q = new URLSearchParams()
    if (params?.limit)    q.set('limit',    String(params.limit))
    if (params?.offset)   q.set('offset',   String(params.offset))
    if (params?.location) q.set('location', params.location)
    return request<HistoryRecord[]>(`/history?${q}`)
  },
}
