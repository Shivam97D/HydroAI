# HydroAI – Frontend Integration Guide

This document is written for the **React / Leaflet** frontend team.

---

## Base URL

| Environment | URL |
|---|---|
| Local dev | `http://localhost:8000` |
| Staging | `https://api-staging.hydroai.example.com` |
| Production | `https://api.hydroai.example.com` |

Interactive API docs (Swagger): `{BASE_URL}/docs`

---

## Endpoints

### `POST /predict`

Run a flood prediction for a location.

**Request**
```json
{
  "location": "Pune"
}
```
Or with explicit coordinates:
```json
{
  "lat": 18.5204,
  "lon": 73.8567
}
```

**Response (Low Risk – simulation not run)**
```json
{
  "location": "Pune",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "risk_score": 0.18,
  "risk_level": "Low",
  "run_simulation": false,
  "flood_map_url": null,
  "geojson_url": null,
  "max_water_depth": null,
  "affected_places": [],
  "insight": "Low flood risk due to moderate rainfall.",
  "features": {
    "rainfall_24h": 8.0,
    "rainfall_3d": 18.0,
    "rainfall_7d": 32.0,
    "elevation": 152.0,
    "river_flow": 45.0
  }
}
```

**Response (High Risk – simulation run)**
```json
{
  "location": "Pune",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "risk_score": 0.78,
  "risk_level": "High",
  "run_simulation": true,
  "flood_map_url": "http://localhost:8000/maps/flood_a3f9c12e44.png",
  "geojson_url": "http://localhost:8000/maps/flood_a3f9c12e44.geojson",
  "max_water_depth": 2.3,
  "affected_places": [
    { "name": "Kothrud",      "water_depth": 1.2 },
    { "name": "Shivajinagar", "water_depth": 1.8 }
  ],
  "insight": "High flood risk due to heavy 24-hour rainfall, low elevation.",
  "features": { ... }
}
```

---

### `GET /health`

```json
{
  "status": "ok",
  "model_loaded": true,
  "database": "ok",
  "version": "1.0.0"
}
```

---

### `GET /history?limit=20&offset=0&location=Pune`

Returns an array of past prediction records (same shape as `/predict` response plus an `id` and `timestamp` field).

---

## React Integration Example

### 1 – Call the API

```tsx
// src/api/hydroai.ts
const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface PredictResponse {
  location: string;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: "Low" | "Medium" | "High";
  run_simulation: boolean;
  flood_map_url: string | null;
  geojson_url: string | null;
  max_water_depth: number | null;
  affected_places: { name: string; water_depth: number }[];
  insight: string;
}

export async function predict(location: string): Promise<PredictResponse> {
  const res = await fetch(`${BASE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ location }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}
```

---

### 2 – Render risk badge

```tsx
const RISK_COLOURS = {
  Low:    "bg-green-500",
  Medium: "bg-yellow-500",
  High:   "bg-red-600",
};

function RiskBadge({ level }: { level: string }) {
  return (
    <span className={`px-3 py-1 rounded-full text-white font-semibold ${RISK_COLOURS[level]}`}>
      {level} Risk
    </span>
  );
}
```

---

### 3 – Leaflet flood map overlay

```tsx
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, ImageOverlay } from "react-leaflet";

function FloodMap({ data }: { data: PredictResponse }) {
  const [geojson, setGeojson] = React.useState(null);

  React.useEffect(() => {
    if (data.geojson_url) {
      fetch(data.geojson_url)
        .then(r => r.json())
        .then(setGeojson);
    }
  }, [data.geojson_url]);

  return (
    <MapContainer
      center={[data.latitude, data.longitude]}
      zoom={13}
      style={{ height: "500px", width: "100%" }}
    >
      {/* Base layer */}
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

      {/* Flood GeoJSON overlay */}
      {geojson && (
        <GeoJSON
          data={geojson}
          style={(feature) => ({
            color: "#1565C0",
            fillColor: depthToColour(feature?.properties?.water_depth),
            weight: 0,
            fillOpacity: 0.65,
          })}
        />
      )}

      {/* Affected place markers */}
      {data.affected_places.map((place) => (
        <Marker key={place.name} position={[data.latitude, data.longitude]}>
          <Popup>
            <strong>{place.name}</strong>
            <br />
            Water depth: {place.water_depth} m
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

function depthToColour(depth: number): string {
  if (depth > 2)   return "#B71C1C";  // dark red
  if (depth > 1)   return "#E53935";  // red
  if (depth > 0.5) return "#FB8C00";  // orange
  return "#FDD835";                   // yellow
}
```

---

### 4 – Affected places sidebar

```tsx
function AffectedPlaces({ places }: { places: { name: string; water_depth: number }[] }) {
  if (!places.length) return <p>No areas severely affected.</p>;

  return (
    <ul className="space-y-2">
      {places.map(p => (
        <li key={p.name} className="flex justify-between items-center border-b pb-1">
          <span className="font-medium">{p.name}</span>
          <span className="text-blue-700">{p.water_depth.toFixed(1)} m</span>
        </li>
      ))}
    </ul>
  );
}
```

---

## CORS

The backend accepts requests from origins listed in the `ALLOWED_ORIGINS`
environment variable (comma-separated).  Set it to match your frontend dev
server URL, e.g. `http://localhost:5173`.

---

## Static Assets

Flood maps and GeoJSON files are served directly at:

```
GET /maps/{filename}
```

Example:
```
GET http://localhost:8000/maps/flood_a3f9c12e44.geojson
GET http://localhost:8000/maps/flood_a3f9c12e44.png
```

No authentication required for map assets.

---

## Error Handling

| HTTP code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (invalid location / coords) |
| 422 | Validation error (malformed JSON body) |
| 500 | Internal server error |

Error body:
```json
{ "detail": "human-readable message" }
```
