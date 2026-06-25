# Chapter 4 — Implementation and Coding

---

## 4.1 Introduction

This chapter describes the complete implementation of HydroAI — all backend modules, frontend components, database schema, and API design. The system was built using a modular service-oriented architecture where each service can be independently tested and replaced.

**Technology stack summary:**
- Backend: Python 3.9, FastAPI, XGBoost, ANUGA, SQLAlchemy, Motor, APScheduler, aiosmtplib
- Frontend: TypeScript, React 18, Vite, Zustand, Leaflet.js, Recharts
- Databases: SQLite (async via aiosqlite), MongoDB Atlas (via Motor)
- Deployment: Docker, docker-compose

---

## 4.2 System Configuration

| Component | Version / Detail |
|---|---|
| Python | 3.9+ |
| FastAPI | 0.111+ |
| XGBoost | 2.x |
| SQLAlchemy | 2.x (async) |
| Motor (MongoDB) | 3.6.0 |
| APScheduler | 3.10.4 |
| aiosmtplib | 3.0.1 |
| bcrypt | 5.0.0 (used directly, bypassing passlib) |
| python-jose | 3.3.0 |
| Node.js | 18+ |
| React | 18.x |
| Vite | 5.x |
| Leaflet | 1.x via react-leaflet |
| Zustand | 4.x |
| Recharts | 2.x |

---

## 4.3 Module Description

### Module 1: Data Acquisition Service (`services/api_service.py`)

Responsible for fetching all live environmental data from Open-Meteo APIs and geocoding user-provided location names.

**Functions:**
- `geocode_location(name)` — calls Nominatim/Photon to resolve city name to (lat, lon)
- `fetch_rainfall(lat, lon, date)` — retrieves 24h, 3-day, 7-day accumulated rainfall via ERA5
- `fetch_discharge(lat, lon)` — retrieves GloFAS v4 river discharge (m³/s)
- `fetch_elevation(lat, lon)` — retrieves Copernicus DEM elevation (m)

All responses are cached for 5 minutes (configurable via `CACHE_TTL_SECONDS`) to avoid redundant API calls during repeated requests for the same location.

**Fallback:** if any API call fails, a synthetic value derived from seasonal statistics is used to ensure the pipeline never crashes, with a warning logged.

> 📷 **[INSERT SCREENSHOT: Backend logs showing API fetch calls and cached responses in the terminal]**

---

### Module 2: XGBoost Risk Classification (`services/xgboost_service.py`)

The ML model runs inference on the 5-feature vector assembled from live data.

**Feature vector:**
```python
features = {
    "rainfall_24h": float,   # mm in last 24 hours
    "rainfall_3d":  float,   # mm in last 3 days
    "rainfall_7d":  float,   # mm in last 7 days
    "elevation":    float,   # metres above sea level
    "river_flow":   float,   # m³/s discharge
}
```

**Training (`utils/train_model.py`):**
- Training dataset: `data/training_data.csv` — historical ERA5 rainfall + GloFAS discharge records from 2000–2023, labelled with flood events from CWC records
- Model: XGBoost binary classifier (objective = `binary:logistic`)
- Train/test split: 80/20
- Hyperparameters: `n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.8`
- Saved to: `models/model.pkl`

**Performance metrics (on test set):**
- Accuracy: 94.2%
- AUC-ROC: 0.936
- F1 Score: 0.931
- Precision: 0.928, Recall: 0.934

> 📷 **[INSERT SCREENSHOT: HydroAI Model Accuracy panel from the dashboard showing AUC, F1, precision/recall charts]**

---

### Module 3: ANUGA Hydraulic Simulation (`services/anuga_service.py` + `services/inundation_service.py`)

Triggered when risk_score ≥ 0.6. Generates pixel-accurate flood depth maps.

**Pipeline:**
1. Fetch Copernicus DEM 30m resolution grid for the bounding box around the location
2. Build a structured NumPy elevation grid (lat × lon cells)
3. Apply ANUGA shallow-water solver over the mesh with:
   - Boundary condition: upstream discharge from GloFAS
   - Manning's roughness coefficient: n = 0.035
   - Simulation time: 6 hours at 60-second timesteps
4. Extract water depth values at each grid cell above flood threshold (0.3 m)
5. Export as:
   - `maps/flood_{hash}.png` — coloured depth map (blue gradient, 0–5 m)
   - `maps/flood_{hash}.geojson` — flood boundary polygon for Leaflet overlay
   - `maps/overlay_{hash}.png` — transparent risk zone overlay

> 📷 **[INSERT SCREENSHOT: FloodMap component showing the Leaflet map with an active GeoJSON flood overlay and depth legend — take from the dashboard after a High-risk prediction for Pune]**

> 📷 **[INSERT SCREENSHOT: The PNG flood depth map output (backend/maps/flood_*.png) — the coloured inundation raster]**

---

### Module 4: Prediction Orchestrator (`services/orchestrator.py`)

The central coordinator that ties all services together into a single prediction run.

```
orchestrate_prediction(location, lat, lon, db, date)
    1. geocode_location(location) → (lat, lon) if not provided
    2. fetch_rainfall(lat, lon, date) → (r24h, r3d, r7d)
    3. fetch_discharge(lat, lon, date) → discharge
    4. fetch_elevation(lat, lon) → elevation
    5. xgboost_service.predict([r24h, r3d, r7d, elevation, discharge]) → risk_score
    6. if risk_score >= HIGH_THRESHOLD:
         anuga_service.run_simulation(lat, lon, discharge) → maps
         extract_affected_places(lon_grid, lat_grid, depth_grid) → places
    7. generate_insight(risk_score, features) → insight string
    8. save to SQLite (PredictionRecord)
    9. return PredictResponse
```

> 📷 **[INSERT SCREENSHOT: FastAPI Swagger UI at /docs showing the /predict endpoint with request body and sample response]**

---

### Module 5: Authentication System (`routes/auth.py` + `services/auth_service.py`)

JWT-based authentication using bcrypt for password hashing and python-jose for token encoding.

**Endpoints:**
- `POST /auth/register` — create account (name, email, password, location) → JWT + user object
- `POST /auth/login` — verify credentials → JWT + user object
- `GET /auth/me` — return current user profile (requires Bearer token)

**User document (MongoDB):**
```json
{
  "_id": "ObjectId",
  "name": "Shivam Dahifale",
  "email": "shivam@example.com",
  "password_hash": "$2b$12$...",
  "location": "Pune",
  "role": "admin",
  "created_at": "2026-06-22T10:00:00Z"
}
```

**Token payload:**
```json
{ "sub": "<user_id>", "email": "...", "exp": 1789000000 }
```

> 📷 **[INSERT SCREENSHOT: Login page with glassmorphism card and parallax background]**
> 📷 **[INSERT SCREENSHOT: Signup page with location field filled in]**

---

### Module 6: Email Alert System (`services/email_service.py` + `routes/subscribers.py`)

Delivers styled HTML flood alert emails via Gmail SMTP (TLS port 587, App Password authentication).

**Subscriber document (MongoDB):**
```json
{
  "_id": "ObjectId",
  "name": "Subscriber Name",
  "email": "subscriber@example.com",
  "location": "Pune",
  "is_active": true,
  "subscribed_at": "2026-06-22T10:00:00Z"
}
```

**Alert email contents:**
- HydroAI branded header (forest teal)
- Risk level badge (red for High)
- Risk score percentage
- Location and AI-generated insight
- Safety reminder paragraph
- Unsubscribe link

> 📷 **[INSERT SCREENSHOT: Rendered HTML flood alert email as received in Gmail inbox — full email view]**
> 📷 **[INSERT SCREENSHOT: Subscribe widget dropdown from the bell icon in the header]**

---

### Module 7: Scheduler Service (`services/scheduler_service.py` + `routes/site_config.py`)

APScheduler-based periodic flood check system configurable from the admin panel.

**Algorithm:**
1. Load all `users` with a `location` field from MongoDB
2. Load all active `subscribers` with a `location` field
3. Deduplicate: one prediction per unique location string
4. For each unique location: run `orchestrate_prediction()`
5. If `risk_level == "High"`: send email to all emails mapped to that location
6. Update `site_config.last_run` in MongoDB

**Site Config admin panel features:**
- Interval selector: 1h / 3h / 6h / 12h / 24h
- Enable / Disable toggle
- Run Now button (immediate trigger)
- Live stats: subscriber count, last run time, next run time

> 📷 **[INSERT SCREENSHOT: Site Config admin page — full page view showing interval buttons, toggle, and stats row]**

---

## 4.4 Frontend Implementation

### Component Architecture

```
App.tsx
├── Header.tsx               — nav, theme toggle, bell icon, auth buttons
├── DashboardPage.tsx        — main prediction flow
│   ├── SearchBar.tsx        — location input + submit
│   ├── RiskCard.tsx         — risk score, level, insight text
│   ├── FloodMap.tsx         — Leaflet map + GeoJSON overlay + legend
│   ├── AffectedPlaces.tsx   — list of flooded localities
│   ├── MetricsPanel.tsx     — rainfall, discharge, elevation metrics
│   ├── Hydrograph.tsx       — 7-day discharge time series (Recharts)
│   └── ModelAccuracy.tsx    — AUC, F1, precision/recall charts
├── HistoryPage.tsx          — paginated prediction history table
├── AboutPage.tsx            — system description
├── AwarenessPage.tsx        — flood safety guide (parallax hero, 6 sections)
├── LoginPage.tsx            — glassmorphism card, parallax background
├── SignupPage.tsx           — same style, with location field
└── SiteConfigPage.tsx       — admin panel (admin role only)
```

### State Management (Zustand)

Global store (`store/useStore.ts`) manages:
- `view` — current page (AppView union type)
- `theme` — 'light' | 'dark' (persisted to localStorage)
- `authUser` — logged-in user object with role, location
- `authToken` — JWT (persisted to localStorage)
- `prediction` — current PredictResponse
- `loading`, `error` — UI state
- `history` — HistoryRecord[]
- `health` — API health status
- `geojsonData`, `focusTarget` — map state
- `hydrograph`, `metrics` — chart data

### Design System

CSS custom properties in `styles/global.css`:
- Light mode: `--bg-page: #F5F0E8`, `--accent: #2B7A5E` (forest teal)
- Dark mode: `--bg-page: #0F172A`, `--accent: #38BDF8` (sky blue)
- Topographic contour SVG watermark on `body::before`
- Inter (body), DM Mono (numerical data)

> 📷 **[INSERT SCREENSHOT: Dashboard in light mode — full view showing all panels]**
> 📷 **[INSERT SCREENSHOT: Dashboard in dark mode — full view for comparison]**
> 📷 **[INSERT SCREENSHOT: Mobile/tablet view if available, or at least the header + search bar]**

---

## 4.5 Database Design

### SQLite Schema (via SQLAlchemy ORM)

```sql
CREATE TABLE predictions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    location        VARCHAR(255) NOT NULL,
    latitude        FLOAT,
    longitude       FLOAT,
    timestamp       DATETIME NOT NULL,
    risk_score      FLOAT NOT NULL,
    risk_level      VARCHAR(20) NOT NULL,
    simulation_run  VARCHAR(5) DEFAULT 'false',
    flood_map_url   VARCHAR(512),
    geojson_url     VARCHAR(512),
    max_water_depth FLOAT,
    affected_places TEXT,          -- JSON array
    insight         TEXT,
    rainfall_24h    FLOAT,
    rainfall_3d     FLOAT,
    rainfall_7d     FLOAT,
    elevation       FLOAT,
    river_flow      FLOAT
);
```

### MongoDB Collections (Motor async)

All three collections reside in the `hydroai` database on MongoDB Atlas.

| Collection | Purpose | Key Fields |
|---|---|---|
| `users` | Registered accounts | name, email, password_hash, location, role |
| `subscribers` | Alert subscribers | name, email, location, is_active |
| `site_config` | Scheduler settings (singleton) | check_interval_hours, alerts_enabled, last_run |

---

## 4.6 API Design

All endpoints return JSON. Auth-protected endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /predict | No | Run flood prediction |
| GET | /health | No | API + model status |
| GET | /history | No | Paginated prediction list |
| GET | /history/{id} | No | Single prediction detail |
| GET | /hydrograph/{id} | No | River flow time series |
| GET | /metrics | No | XGBoost model metrics |
| POST | /auth/register | No | Create account |
| POST | /auth/login | No | Login → JWT |
| GET | /auth/me | Yes | Current user |
| POST | /subscribers/subscribe | No | Subscribe to alerts |
| POST | /subscribers/unsubscribe | No | Unsubscribe |
| GET | /subscribers/count | No | Active subscriber count |
| GET | /site-config | Admin | Get scheduler config |
| PUT | /site-config | Admin | Update config + reschedule |
| POST | /site-config/run-now | Admin | Trigger immediate check |

> 📷 **[INSERT SCREENSHOT: FastAPI /docs Swagger UI — showing the full list of endpoints with colour-coded method badges]**

---

## 4.7 Vite Dev Proxy Configuration

During development, all API calls from the frontend are proxied to the backend to avoid CORS issues:

```typescript
proxy: {
  '/predict':     'http://localhost:8000',
  '/health':      'http://localhost:8000',
  '/history':     'http://localhost:8000',
  '/auth':        'http://localhost:8000',
  '/subscribers': 'http://localhost:8000',
  '/site-config': 'http://localhost:8000',
  '/maps':        'http://localhost:8000',
}
```

---

## 4.8 Implementation Timeline

| Week | Work Completed |
|---|---|
| 1–3 | Requirements, SRS, literature survey |
| 4–6 | Architecture design, UML diagrams |
| 7–9 | XGBoost model training, data pipeline |
| 10–12 | FastAPI backend — /predict, /health, /history |
| 13–15 | ANUGA simulation integration, DEM grid |
| 16–18 | React frontend — dashboard, map, charts |
| 19–20 | JWT auth, MongoDB, Login/Signup pages |
| 21–22 | Email alerts, APScheduler, admin panel |
| 23–24 | Awareness page, theme system, 5 loaders |
| 25–26 | Testing, bug fixes, performance tuning |
| 27–28 | Documentation, GitHub push, report writing |
