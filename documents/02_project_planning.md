# Chapter 2 — Project Planning and Management

---

## 2.1 Introduction

This chapter describes the project planning and management framework followed during the development of HydroAI. It covers the System Requirement Specification (SRS), the SDLC process model, cost and effort estimates, and the project schedule. All planning decisions were validated against the final implemented system.

---

## 2.2 System Requirement Specification (SRS)

### 2.2.1 System Overview

HydroAI predicts flood inundation by combining a trained XGBoost risk classifier with an ANUGA hydraulic simulation engine. The system automatically fetches live environmental data from open APIs, runs the prediction pipeline, and presents results through a web-based dashboard.

**Data inputs (all fetched automatically):**
- 7-day ERA5 rainfall accumulation (mm) — Open-Meteo Forecast API
- Historical rainfall for date-replay mode — Open-Meteo Archive API
- GloFAS v4 river discharge (m³/s) — Open-Meteo Flood API
- Copernicus DEM elevation (m) — Open-Meteo Elevation API
- Geocoordinates — Nominatim / Photon geocoding

> 📷 **[INSERT DIAGRAM: System Overview / data-flow block diagram — box showing APIs → Backend Pipeline → Dashboard]**

---

### 2.2.2 Functional Requirements

| ID | Requirement | Description |
|---|---|---|
| FR1 | Location Input | Accept a city/area name or lat-lon coordinates; geocode automatically |
| FR2 | Data Fetch | Automatically retrieve ERA5 rainfall, GloFAS discharge, and DEM elevation |
| FR3 | Risk Classification | Run XGBoost model; output risk score (0–1) and level (Low / Medium / High) |
| FR4 | Hydrodynamic Simulation | Trigger ANUGA 2D shallow-water simulation for High-risk predictions |
| FR5 | Flood Map Generation | Produce PNG flood depth image and GeoJSON flood boundary overlay |
| FR6 | Dashboard Visualisation | Display risk card, flood map, affected places, hydrograph on Leaflet.js map |
| FR7 | Prediction History | Persist all prediction runs in SQLite; expose paginated history view |
| FR8 | User Authentication | Register / login with JWT; persist session across browser restarts |
| FR9 | Email Alert Subscription | Subscribe with name, email, and city; receive HTML flood alert emails |
| FR10 | Scheduled Flood Checks | APScheduler cron job: one prediction per unique subscriber location at configured interval |
| FR11 | Admin Site Config | Admin can set check interval (1h/3h/6h/12h/24h), enable/disable alerts, trigger manual run |
| FR12 | Awareness Page | Static flood safety guide with animated sections and emergency contacts |

---

### 2.2.3 Non-Functional Requirements

| Category | Requirement | Target |
|---|---|---|
| Performance | Prediction response time | < 30 seconds (API fetch + XGBoost) |
| Performance | Simulation time (ANUGA) | < 5 minutes for regional DEM grid |
| Accuracy | Nash–Sutcliffe Efficiency | NSE ≥ 0.85 |
| Accuracy | Root Mean Square Error | RMSE ≤ 0.5 m |
| Accuracy | AUC (ROC) | ≥ 0.90 |
| Reliability | Uptime | 99% (graceful degradation if external APIs unavailable) |
| Scalability | Multi-location support | Unlimited locations via geocoding |
| Usability | Dashboard responsiveness | Works on 1280px+ screens; mobile-friendly |
| Security | Authentication | JWT with 7-day expiry; bcrypt password hashing |
| Security | Role-based access | Admin-only site config; user-only profile |
| Maintainability | Modular architecture | Services independently replaceable (swap ANUGA, swap ML model) |
| Availability | Scheduled jobs | APScheduler persists interval in MongoDB across restarts |

---

### 2.2.4 Deployment Environment

| Component | Specification |
|---|---|
| Operating System | macOS / Linux / Windows (Docker) |
| Primary Language | Python 3.9+ (backend), TypeScript (frontend) |
| Backend Framework | FastAPI (async, ASGI) |
| Frontend Framework | React 18 + Vite |
| ML Engine | XGBoost 2.x |
| Simulation Engine | ANUGA Hydro (Python) |
| Primary Database | SQLite via SQLAlchemy + aiosqlite (history) |
| Secondary Database | MongoDB Atlas via Motor async driver (users, subscribers, config) |
| Email | Gmail SMTP via aiosmtplib + App Password |
| Scheduler | APScheduler 3.x (AsyncIOScheduler) |
| Map Tiles | CartoDB Voyager (light) / Esri Satellite |
| Cloud Deployment | Docker + docker-compose (AWS / GCP / Render) |
| Hardware (dev) | 8 GB RAM, multi-core CPU, 20 GB storage |
| Hardware (prod) | 4 vCPU, 8 GB RAM cloud VM |

---

### 2.2.5 External Interface Requirements

**User Interface**
- Web dashboard with: Search bar, Risk card, Leaflet flood map, Affected places panel, Hydrograph chart, Model accuracy panel
- Login / Signup pages with parallax background animation
- Flood Awareness page with scroll-triggered animated sections
- Admin Site Config page with interval selector, enable/disable toggle, live stats

> 📷 **[INSERT SCREENSHOT: Full HydroAI dashboard — annotated with panel labels]**

**Software Interfaces**
- Open-Meteo REST APIs (forecast, archive, flood, elevation) — no auth required
- Nominatim/Photon geocoding REST API
- MongoDB Atlas connection string (Motor async driver)
- Gmail SMTP (TLS port 587, App Password auth)

**Hardware Interface**
- Standard internet-connected server; no IoT hardware required in current version

---

## 2.3 Project Process Model

The development followed the **Incremental Model** of SDLC, with each increment being a fully working subsystem. This allowed early testing of the core prediction pipeline while UI and alert features were built in parallel.

**Increment 1 — Core Prediction Pipeline**
- XGBoost model training on ERA5 + GloFAS historical data
- FastAPI `/predict` endpoint with live data fetch
- Basic HTML response

**Increment 2 — Frontend Dashboard**
- React + Vite setup, Zustand state management
- Leaflet map with flood overlay, risk card, hydrograph

**Increment 3 — ANUGA Simulation**
- Copernicus DEM inundation grid
- GeoJSON flood boundary generation, PNG depth map

**Increment 4 — Auth + Alert System**
- JWT authentication (register / login / me)
- MongoDB subscriber store
- Gmail SMTP alert emails

**Increment 5 — Scheduler + Admin Panel**
- APScheduler periodic flood checks
- Admin Site Config page (interval, enable/disable, run-now)
- GitHub deployment

> 📷 **[INSERT DIAGRAM: Incremental SDLC timeline — 5 horizontal bars with milestone markers]**

---

## 2.4 Cost and Effort Estimation

### COCOMO Semi-Detached Model

All software used is open-source or free-tier cloud; primary cost is developer time.

**Assumptions:**
- Estimated Source Lines of Code: ~15,000 (Python backend + TypeScript frontend)
- Team size: 4 members
- Development duration: ~28 weeks (Sem I + Sem II)

**COCOMO Equations:**

```
E  = 3.0 × (KLOC)^1.12    [Effort, man-months]
D  = 2.5 × (E)^0.35       [Duration, months]
P  = E / D                 [People required]
```

**Calculation:**
- KLOC = 15
- E = 3.0 × (15)^1.12 = **58.1 man-months**
- D = 2.5 × (58.1)^0.35 = **9.8 months**
- P = 58.1 / 9.8 ≈ **5.9 → 4 members (adjusted for academic project)**

### Cost Estimate Table

| Parameter | Value |
|---|---|
| Project Class | Semi-Detached |
| Estimated KLOC | 15 |
| Estimated Effort | 58.1 man-months |
| Development Duration | ~9.8 months |
| Team Size | 4 |
| Software Cost | ₹0 (all open-source) |
| Cloud (dev, free tier) | ₹0 |
| Estimated Manpower Cost | ₹50,000 (notional @ ₹860/man-month) |

### Function Point Analysis

| Component | Count | Complexity | UFP |
|---|---|---|---|
| External Inputs (predict, register, login, subscribe, site-config) | 5 | Medium | 20 |
| External Outputs (risk card, flood map, GeoJSON, email, hydrograph) | 5 | High | 35 |
| External Queries (history, health, me, metrics, awareness) | 5 | Low | 15 |
| Internal Logical Files (SQLite history, MongoDB users, MongoDB subscribers, site_config) | 4 | Medium | 28 |
| External Interface Files (Open-Meteo APIs × 4, Nominatim, Gmail) | 6 | Medium | 30 |
| **Total UFP** | | | **128** |
| VAF (Value Adjustment Factor, 14 complexity factors) | | | 1.15 |
| **AFP = UFP × VAF** | | | **147.2** |

---

## 2.5 Project Scheduling

### Phase Timeline

| Phase | Activities | Duration | Status |
|---|---|---|---|
| Phase 1 | Requirements, SRS, Literature Survey | Weeks 1–3 | ✅ Complete |
| Phase 2 | Architecture design, UML diagrams | Weeks 4–6 | ✅ Complete |
| Phase 3 | XGBoost model training, `/predict` API | Weeks 7–10 | ✅ Complete |
| Phase 4 | ANUGA simulation integration, DEM grid | Weeks 11–14 | ✅ Complete |
| Phase 5 | React frontend, Leaflet map, dashboard | Weeks 15–18 | ✅ Complete |
| Phase 6 | Auth system (JWT + MongoDB) | Weeks 19–20 | ✅ Complete |
| Phase 7 | Email alerts, APScheduler, Admin panel | Weeks 21–23 | ✅ Complete |
| Phase 8 | Testing, validation, bug fixes | Weeks 24–26 | ✅ Complete |
| Phase 9 | Documentation, GitHub, report writing | Weeks 27–28 | ✅ Complete |

> 📷 **[INSERT DIAGRAM: Gantt chart — horizontal bars per phase across 28 weeks, colour-coded by status]**

### Team Responsibilities

| Member | Primary Role |
|---|---|
| Shivam Goraksha Dahifale | Backend lead — FastAPI, XGBoost, ANUGA, scheduler, auth |
| Sanidhya Rishiraj Naik | ML pipeline — model training, ERA5/GloFAS data integration |
| Janhavi Abhijit Lonari | Frontend lead — React, Leaflet, UI/UX design system |
| Onkar Rajendra Gaikwad | Testing, documentation, deployment, email alert system |
