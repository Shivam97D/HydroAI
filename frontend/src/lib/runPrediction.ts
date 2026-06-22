import { api } from '../api/hydroai'
import { useStore } from '../store/useStore'

/**
 * Shared prediction action used by the search bar and by deep-links
 * (?location=Pune&date=2019-08-05). Fetches the prediction, then the flood
 * GeoJSON layer and the discharge hydrograph.
 */
export async function runPrediction(location: string, date?: string) {
  const s = useStore.getState()
  const loc = location.trim()
  if (!loc || s.loading) return

  s.setLoading(true)
  s.setError(null)
  s.setPrediction(null)
  s.setGeojsonData(null)
  s.setHydrograph(null)
  s.setFocusTarget(null)

  try {
    const result = await api.predict({ location: loc, date })
    s.setPrediction(result)

    if (result.geojson_url) {
      const gj = await fetch(result.geojson_url).then(r => r.json()).catch(() => null)
      if (gj) s.setGeojsonData(gj)
    }

    api.hydrograph({ lat: result.latitude, lon: result.longitude })
      .then(s.setHydrograph)
      .catch(() => s.setHydrograph(null))
  } catch (err: any) {
    s.setError(err?.message ?? 'Prediction failed')
  } finally {
    s.setLoading(false)
  }
}
