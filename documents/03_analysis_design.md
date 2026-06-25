# Chapter 3 — Analysis and Design

---

## 3.1 Introduction

This chapter presents the complete analysis and design of HydroAI, covering the IDEA matrix, mathematical models, feasibility analysis, system architecture, and all UML diagrams. The design directly maps to the implemented system described in Chapter 4.

---

## 3.2 IDEA Matrix

| Factor | Description |
|---|---|
| **I — Identify** | India faces annual flood disasters causing loss of life and property. Existing forecasting tools are expensive, slow, or inaccessible to local disaster management bodies. |
| **D — Define** | Build an open-source, real-time flood risk platform that combines physics-based ANUGA simulation with ML-based XGBoost risk classification, served through a web dashboard. |
| **E — Explore** | Evaluated HEC-RAS (licensed), MIKE-FLOOD (licensed), standalone ML approaches, and ANUGA (open-source). Chose hybrid XGBoost + ANUGA for best accuracy-vs-cost tradeoff. |
| **A — Act** | Implemented the full-stack system: FastAPI backend, React frontend, MongoDB auth/subscribers, APScheduler alerts, and deployed to GitHub. |

---

## 3.3 Mathematical Model

### 3.3.1 Saint-Venant Shallow-Water Equations (ANUGA)

ANUGA solves the 2D depth-averaged Saint-Venant equations over an unstructured triangular mesh:

**Continuity equation:**
```
∂h/∂t + ∂(hu)/∂x + ∂(hv)/∂y = 0
```

**Momentum equations (x and y):**
```
∂(hu)/∂t + ∂(hu² + ½gh²)/∂x + ∂(huv)/∂y = gh(S₀ₓ - Sfₓ)
∂(hv)/∂t + ∂(huv)/∂x + ∂(hv² + ½gh²)/∂y = gh(S₀ᵧ - Sfᵧ)
```

Where:
- h = water depth (m)
- u, v = depth-averaged velocity components (m/s)
- g = gravitational acceleration (9.81 m/s²)
- S₀ = bed slope
- Sf = friction slope (Manning's equation)

**Manning's friction:**
```
Sf = n²V²/h^(4/3)
```
Where n = Manning's roughness coefficient (0.035 for natural channels).

### 3.3.2 XGBoost Risk Classification

The XGBoost model is trained on historical ERA5 rainfall + GloFAS discharge data with binary labels (flood / no-flood) derived from CWC flood records.

**Feature vector:**
```
X = [rainfall_24h, rainfall_3d, rainfall_7d, elevation, river_flow]
```

**Risk classification:**
```
risk_score = XGBoost.predict_proba(X)[1]  ∈ [0, 1]

Risk Level:
  Low    if risk_score < 0.3
  Medium if 0.3 ≤ risk_score < 0.6
  High   if risk_score ≥ 0.6
```

**Objective function (XGBoost):**
```
L = Σ[yᵢ log(ŷᵢ) + (1 - yᵢ) log(1 - ŷᵢ)] + Ω(f)
```
Where Ω(f) is the regularisation term penalising model complexity.

### 3.3.3 COCOMO Effort Model

```
E = 3.0 × (KLOC)^1.12 = 58.1 man-months
D = 2.5 × (E)^0.35    = 9.8 months
```

---

## 3.4 Feasibility Analysis

| Dimension | Assessment |
|---|---|
| **Technical** | ✅ All tools open-source and proven (FastAPI, XGBoost, ANUGA, React, MongoDB Atlas free tier). No proprietary dependencies. |
| **Economic** | ✅ Zero software licensing cost. Cloud hosting on free-tier VMs (Render/Railway). Developer time is the only cost. |
| **Operational** | ✅ Web-based dashboard requires no specialist software on user's machine. Email alerts require no user action after subscription. |
| **Legal** | ✅ All data sources (Open-Meteo, Nominatim) provide free public data under open licences. ANUGA is Apache 2.0 licensed. |
| **Schedule** | ✅ Completed within 28-week academic calendar using Incremental SDLC model. |

---

## 3.5 System Architecture

HydroAI follows a **three-tier architecture**: browser client → FastAPI server → data stores + external APIs.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PRESENTATION TIER                               │
│         React 18 + TypeScript + Vite (localhost:5173)              │
│  ┌──────────────┐ ┌────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Dashboard   │ │  Auth Pages│ │  Awareness  │ │ Site Config │ │
│  │  (Leaflet    │ │  Login /   │ │  (Safety    │ │  (Admin     │ │
│  │   FloodMap)  │ │  Signup)   │ │   Guide)    │ │   Panel)    │ │
│  └──────────────┘ └────────────┘ └─────────────┘ └─────────────┘ │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP REST / Vite Proxy
┌───────────────────────────▼─────────────────────────────────────────┐
│                     APPLICATION TIER                                │
│              FastAPI (Python 3.9+, localhost:8000)                 │
│  ┌────────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────────┐  │
│  │ /predict   │ │ /auth    │ │/subscribers│ │ /site-config     │  │
│  │ /history   │ │ /health  │ │/history    │ │ APScheduler      │  │
│  └────────────┘ └──────────┘ └───────────┘ └──────────────────┘  │
│  ┌────────────────────┐   ┌────────────────────────────────────┐  │
│  │  XGBoost Service   │   │  ANUGA Simulation Service          │  │
│  │  (risk_score, level│   │  (2D SWE, DEM grid, GeoJSON/PNG)  │  │
│  └────────────────────┘   └────────────────────────────────────┘  │
└───────┬─────────────────────────┬──────────────────────────────────┘
        │                         │
┌───────▼──────────┐   ┌──────────▼────────────────────────────────┐
│   DATA TIER      │   │           EXTERNAL APIs                   │
│ SQLite (history) │   │  Open-Meteo: ERA5, GloFAS, Elevation      │
│ MongoDB Atlas:   │   │  Nominatim: Forward geocoding             │
│  - users         │   │  Gmail SMTP: Alert email delivery         │
│  - subscribers   │   └───────────────────────────────────────────┘
│  - site_config   │
└──────────────────┘
```

> 📷 **[INSERT DIAGRAM: Redraw above as a clean architecture diagram with boxes, arrows, and tier labels — use draw.io or Lucidchart. Export as PNG and insert here]**

---

## 3.6 UML Diagrams

### 3.6.1 Use-Case Diagram

**Actors:** Guest User, Registered User, Admin, Scheduler (system actor)

**Use cases:**

| Actor | Use Cases |
|---|---|
| Guest | Search location, View flood prediction, Subscribe to alerts, View awareness page |
| Registered User | All Guest use cases + Login/Signup, View prediction history, Receive personalised alerts |
| Admin | All Registered User use cases + Configure alert schedule, View subscriber count, Trigger manual check |
| Scheduler | Run periodic flood check, Send alert emails (system-initiated) |

> 📷 **[INSERT DIAGRAM: Use-Case UML diagram — draw with actors on sides, use-case ovals in centre, include/extend relationships. Tools: draw.io, StarUML, or PlantUML]**

**PlantUML source (for reference):**
```plantuml
@startuml
left to right direction
actor "Guest" as G
actor "Registered User" as U
actor "Admin" as A
actor "Scheduler" as S

rectangle HydroAI {
  usecase "Search Location" as UC1
  usecase "View Prediction" as UC2
  usecase "Subscribe Alerts" as UC3
  usecase "View Awareness" as UC4
  usecase "Login / Signup" as UC5
  usecase "View History" as UC6
  usecase "Configure Schedule" as UC7
  usecase "Trigger Manual Check" as UC8
  usecase "Run Flood Check" as UC9
  usecase "Send Alert Email" as UC10
}

G --> UC1; G --> UC2; G --> UC3; G --> UC4
U --> UC5; U --> UC6; U --|> G
A --> UC7; A --> UC8; A --|> U
S --> UC9; UC9 ..> UC10 : <<include>>
@enduml
```

---

### 3.6.2 Activity Diagram — Prediction Flow

**Flow:**
1. User enters location → geocoding API resolves lat/lon
2. System fetches ERA5 rainfall (24h, 3d, 7d), GloFAS discharge, DEM elevation
3. XGBoost model scores risk → assigns Low / Medium / High
4. **[Decision]** risk_score ≥ 0.6?
   - **No** → return risk card + hydrograph + model metrics
   - **Yes** → trigger ANUGA simulation → generate flood depth map → render GeoJSON overlay + affected places
5. Save prediction record to SQLite
6. **[Decision]** subscribers exist for this location?
   - **Yes** → send HTML alert email via Gmail SMTP
7. Return complete response to dashboard

> 📷 **[INSERT DIAGRAM: Activity diagram with swim-lanes: User / Backend / External APIs / ANUGA. Include the branching on risk level and the email path]**

---

### 3.6.3 Class Diagram

**Key classes:**

| Class | Attributes | Methods |
|---|---|---|
| `PredictRequest` | location, lat, lon, date | validate() |
| `PredictResponse` | location, latitude, longitude, risk_score, risk_level, run_simulation, flood_map_url, geojson_url, affected_places, insight, features | — |
| `PredictionRecord` (ORM) | id, location, latitude, longitude, timestamp, risk_score, risk_level, simulation_run, flood_map_url, insight | to_dict() |
| `XGBoostService` | model (pkl) | load_model(), predict(features) → float |
| `AnugaService` | settings | run_simulation(lat, lon, discharge) → dict |
| `Orchestrator` | — | orchestrate_prediction(location, lat, lon, db, date) → PredictResponse |
| `ApiService` | _cache | geocode_location(name), fetch_rainfall(lat, lon), fetch_discharge(lat, lon), fetch_elevation(lat, lon) |
| `AuthService` | — | hash_password(plain), verify_password(plain, hash), create_access_token(data), decode_token(token) |
| `EmailService` | settings | send_email(to, subject, html), flood_alert_html(...), welcome_email_html(name) |
| `SchedulerService` | scheduler | start_scheduler(hours), reschedule(hours), run_flood_checks() |
| `User` (MongoDB) | id, name, email, password_hash, location, role, created_at | — |
| `Subscriber` (MongoDB) | id, name, email, location, is_active, subscribed_at | — |
| `SiteConfig` (MongoDB) | _id="main", check_interval_hours, alerts_enabled, last_run | — |

> 📷 **[INSERT DIAGRAM: Class diagram with boxes for each class, attributes and methods listed, arrows showing associations (Orchestrator uses XGBoostService, AnugaService, ApiService)]**

---

### 3.6.4 ER Diagram

**Entities and relationships:**

**SQLite (relational):**
- `predictions` table: id PK, location, latitude, longitude, timestamp, risk_score, risk_level, simulation_run, flood_map_url, geojson_url, max_water_depth, affected_places (JSON), insight, rainfall_24h, rainfall_3d, rainfall_7d, elevation, river_flow

**MongoDB (document):**
- `users` collection: { _id, name, email, password_hash, location, role, created_at }
- `subscribers` collection: { _id, name, email, location, is_active, subscribed_at }
- `site_config` collection: { _id: "main", check_interval_hours, alerts_enabled, last_run, updated_at }

**Relationships:**
- A `user` can subscribe (email present in `subscribers`) — optional link
- `site_config` is a singleton document controlling scheduler behaviour
- `predictions` records are independent (no foreign keys to users in current version)

> 📷 **[INSERT DIAGRAM: ER diagram showing the SQLite predictions table and the three MongoDB collections with field listings and relationship arrows]**

---

### 3.6.5 Sequence Diagram — Flood Prediction Request

```
User → Frontend → Backend(/predict) → ApiService → Open-Meteo
                                                 ← [rainfall, discharge, elevation]
                              → XGBoostService   ← [risk_score]
                              → AnugaService (if High)  ← [geojson, png]
                              → SQLite (save record)
                ← PredictResponse (JSON)
       ← Dashboard render (risk card, map, hydrograph)
```

> 📷 **[INSERT DIAGRAM: Sequence diagram with lifelines: User, Browser, FastAPI, ApiService, XGBoost, ANUGA, SQLite, MongoDB. Show message arrows with labels and return values]**

---

### 3.6.6 Sequence Diagram — Subscriber Alert (Scheduler)

```
APScheduler → SchedulerService.run_flood_checks()
           → MongoDB.find(subscribers with location)
           → Group by unique location
           → [for each location] Orchestrator.orchestrate_prediction()
               → ApiService / XGBoost / ANUGA (same as above)
           → [if High risk] EmailService.send_email() → Gmail SMTP
                                                      → Subscriber inbox
           → MongoDB.update(site_config.last_run)
```

> 📷 **[INSERT DIAGRAM: Sequence diagram for scheduler flow — APScheduler → Backend → Gmail → Subscriber]**

---

### 3.6.7 State Machine Diagram — Prediction Lifecycle

**States:**
1. `IDLE` → user enters location
2. `FETCHING_DATA` → Open-Meteo API calls in progress
3. `CLASSIFYING` → XGBoost inference running
4. `SIMULATING` → ANUGA running (only if High risk)
5. `SAVING` → writing to SQLite
6. `COMPLETE` → result displayed on dashboard
7. `ERROR` → API failure or model error (graceful fallback with synthetic data)

**Transitions:**
- IDLE → FETCHING_DATA: on search submit
- FETCHING_DATA → CLASSIFYING: on data received
- CLASSIFYING → SIMULATING: if risk_score ≥ 0.6
- CLASSIFYING → SAVING: if risk_score < 0.6
- SIMULATING → SAVING: on simulation complete
- SAVING → COMPLETE: on DB write success
- Any state → ERROR: on unhandled exception

> 📷 **[INSERT DIAGRAM: State machine diagram with rounded boxes for each state, labelled transition arrows]**

---

### 3.6.8 Deployment Diagram

**Nodes:**
- **Developer Machine / Cloud VM** → runs FastAPI backend (Python, port 8000), serves `/maps` static files
- **MongoDB Atlas Cloud** → hosts users, subscribers, site_config collections
- **Browser (Client)** → runs React SPA (Vite dev: port 5173 / Nginx production)
- **Gmail SMTP Server** → receives outbound alert emails from backend
- **Open-Meteo API Servers** → provide rainfall, discharge, elevation data

> 📷 **[INSERT DIAGRAM: Deployment diagram — server nodes as boxes with components inside, connected by labelled communication paths (HTTPS, SMTP, MongoDB wire protocol)]**
