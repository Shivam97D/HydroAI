import { create } from 'zustand'
import { PredictResponse, HistoryRecord, HealthResponse, Hydrograph, ModelMetrics } from '../api/hydroai'

export type AppView = 'dashboard' | 'history' | 'about' | 'login' | 'signup' | 'awareness' | 'siteconfig'
export type Theme = 'light' | 'dark'

interface HydroStore {
  // ── Theme ────────────────────────────────────────────────────────────────
  theme: Theme
  setTheme: (t: Theme) => void

  // ── Auth ──────────────────────────────────────────────────────────────────
  authUser: { id: string; name: string; email: string; location: string; role: string } | null
  authToken: string | null
  setAuthUser: (u: { id: string; name: string; email: string; location: string; role: string } | null) => void
  setAuthToken: (t: string | null) => void
  logout: () => void

  // ── Current prediction ──────────────────────────────────────────────────
  prediction: PredictResponse | null
  setPrediction: (p: PredictResponse | null) => void

  // ── Loading / error ─────────────────────────────────────────────────────
  loading: boolean
  setLoading: (v: boolean) => void
  error: string | null
  setError: (e: string | null) => void

  // ── History ─────────────────────────────────────────────────────────────
  history: HistoryRecord[]
  setHistory: (h: HistoryRecord[]) => void
  historyLoading: boolean
  setHistoryLoading: (v: boolean) => void

  // ── Health ──────────────────────────────────────────────────────────────
  health: HealthResponse | null
  setHealth: (h: HealthResponse | null) => void

  // ── Navigation ──────────────────────────────────────────────────────────
  view: AppView
  setView: (v: AppView) => void

  // ── Map state ───────────────────────────────────────────────────────────
  activeTab: 'map' | 'image'
  setActiveTab: (t: 'map' | 'image') => void
  geojsonData: GeoJSON.FeatureCollection | null
  setGeojsonData: (g: GeoJSON.FeatureCollection | null) => void

  // Map focus target — clicking an affected area flies the map here.
  // `nonce` forces a re-fly even when the same place is clicked twice.
  focusTarget: { lat: number; lon: number; name: string; nonce: number } | null
  setFocusTarget: (t: { lat: number; lon: number; name: string } | null) => void

  // ── Hydrograph + model metrics ──────────────────────────────────────────
  hydrograph: Hydrograph | null
  setHydrograph: (h: Hydrograph | null) => void
  metrics: ModelMetrics | null
  setMetrics: (m: ModelMetrics | null) => void
}

export const useStore = create<HydroStore>((set) => ({
  theme: (localStorage.getItem('hydroai-theme') as Theme) ?? 'light',
  setTheme: (t) => {
    localStorage.setItem('hydroai-theme', t)
    document.documentElement.setAttribute('data-theme', t)
    set({ theme: t })
  },

  authUser: JSON.parse(localStorage.getItem('hydroai-user') ?? 'null'),
  authToken: localStorage.getItem('hydroai-token'),
  setAuthUser: (u) => { localStorage.setItem('hydroai-user', JSON.stringify(u)); set({ authUser: u }) },
  setAuthToken: (t) => { if (t) localStorage.setItem('hydroai-token', t); else localStorage.removeItem('hydroai-token'); set({ authToken: t }) },
  logout: () => { localStorage.removeItem('hydroai-token'); localStorage.removeItem('hydroai-user'); set({ authUser: null, authToken: null, view: 'dashboard' }) },

  prediction: null,
  setPrediction: (p) => set({ prediction: p }),

  loading: false,
  setLoading: (v) => set({ loading: v }),
  error: null,
  setError: (e) => set({ error: e }),

  history: [],
  setHistory: (h) => set({ history: h }),
  historyLoading: false,
  setHistoryLoading: (v) => set({ historyLoading: v }),

  health: null,
  setHealth: (h) => set({ health: h }),

  view: 'dashboard',
  setView: (v) => set({ view: v }),

  activeTab: 'map',
  setActiveTab: (t) => set({ activeTab: t }),
  geojsonData: null,
  setGeojsonData: (g) => set({ geojsonData: g }),

  focusTarget: null,
  setFocusTarget: (t) =>
    set({ focusTarget: t ? { ...t, nonce: Date.now() } : null }),

  hydrograph: null,
  setHydrograph: (h) => set({ hydrograph: h }),
  metrics: null,
  setMetrics: (m) => set({ metrics: m }),
}))
