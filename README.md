# HydroAI — Flood Intelligence Platform

> Real-time flood prediction, hydrodynamic simulation, and subscriber alert system.  
> BE Final Year Project — Sinhgad College of Engineering, Pune — Group 46.

---

## Overview

HydroAI combines machine learning with hydrodynamic modelling to deliver actionable flood risk intelligence for any location. It fetches live rainfall and river-discharge data, runs an XGBoost risk classifier, optionally triggers an ANUGA hydraulic simulation for high-risk events, and renders interactive flood maps in the browser — all in seconds.

### Key capabilities

| Capability | Detail |
|---|---|
| **Live flood prediction** | ERA5 rainfall + GloFAS river discharge → XGBoost risk score |
| **Hydraulic simulation** | ANUGA inundation model generates pixel-accurate flood depth maps |
| **Interactive map** | Leaflet + GeoJSON overlays, affected-place drill-down, satellite toggle |
| **Hydrograph** | 7-day river-flow time series per prediction |
| **Model accuracy panel** | Real-time XGBoost metrics (accuracy, F1, AUC) |
| **Prediction history** | SQLite log of every run with full replay |
| **Auth system** | JWT + MongoDB — register, login, persistent sessions |
| **Email alerts** | Gmail SMTP — styled HTML flood-alert emails |
| **Scheduled checks** | APScheduler fires one prediction per unique subscriber location, alerts on High risk only |
| **Admin site config** | Configurable check interval (1 h → 24 h), enable/disable, run-now |
| **Awareness page** | Flood safety guide with animated sections, emergency contacts, subscribe CTA |
| **Dark / light mode** | Manual toggle, persisted to localStorage |

---

## Tech Stack

### Backend
- **FastAPI** — async REST API
- **XGBoost** — flood risk classification (trained on real ERA5 + GloFAS historical data)
- **ANUGA** — hydraulic inundation simulation engine
- **SQLAlchemy + aiosqlite** — async SQLite for prediction history
- **Motor** — async MongoDB driver for users, subscribers, site config
- **APScheduler** — periodic scheduled flood checks
- **aiosmtplib** — async Gmail SMTP for alert emails
- **python-jose + bcrypt** — JWT auth and password hashing
- **Open-Meteo APIs** — live rainfall (ERA5), GloFAS discharge, Copernicus DEM (all free, no key)

### Frontend
- **React 18 + TypeScript + Vite**
- **Zustand** — global state
- **Leaflet + react-leaflet** — interactive flood map
- **Recharts** — hydrograph and accuracy charts
- **CSS Modules** — scoped styles with CSS custom-property design tokens
- **Inter + DM Mono** — typography

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     Browser  (React + Vite)                       │
│  Dashboard │ History │ Awareness │ Login/Signup │ Site Config     │
└──────────────────────┬───────────────────────────────────────────┘
                        │  HTTP / Vite proxy
┌──────────────────────▼───────────────────────────────────────────┐
│                   FastAPI  (Python 3.9+)                          │
│                                                                   │
│  /predict  /health  /history  /insights                          │
│  /auth     /subscribers  /site-config                            │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │  XGBoost    │  │ ANUGA Sim   │  │  APScheduler         │    │
│  │  Risk Model │  │ Inundation  │  │  Periodic checks      │    │
│  └─────────────┘  └─────────────┘  └──────────────────────┘    │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │  SQLite DB  │  │  MongoDB    │  │  Gmail SMTP          │    │
│  │  (history)  │  │ (users/subs)│  │  (alert emails)      │    │
│  └─────────────┘  └─────────────┘  └──────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                              │
             ┌────────────────┼─────────────────┐
             │                │                 │
    Open-Meteo ERA5    GloFAS Flood API   Copernicus DEM
    (rainfall data)   (river discharge)  (elevation tiles)
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- [MongoDB Atlas](https://cloud.mongodb.com) free cluster
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) enabled

### 1. Clone

```bash
git clone https://github.com/<your-username>/HydroAI.git
cd HydroAI
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then fill in MongoDB URI, JWT secret, Gmail credentials
python app.py
# API → http://localhost:8000
# Swagger docs → http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# App → http://localhost:5173
```

### 4. Make yourself admin

After registering via the Sign Up page, edit `make_admin.py` to set your email, then:

```bash
cd backend && source venv/bin/activate && python make_admin.py
```

The **Site Config** tab will appear in the nav for your account.

---

## Project Structure

```
HydroAI/
├── backend/
│   ├── app.py                    # FastAPI app factory + lifespan
│   ├── config.py                 # Pydantic settings (reads .env)
│   ├── .env.example              # Config template — copy to .env
│   ├── make_admin.py             # One-time admin promotion script
│   ├── requirements.txt
│   ├── database/
│   │   ├── db.py                 # SQLAlchemy async engine + ORM
│   │   └── mongo.py              # Motor async MongoDB client
│   ├── models/
│   │   ├── model.pkl             # Trained XGBoost classifier
│   │   ├── runoff_model.pkl      # Runoff regression model
│   │   ├── metrics.json          # Model evaluation metrics
│   │   └── thresholds.json       # Risk score thresholds
│   ├── routes/
│   │   ├── auth.py               # Register / Login / Me
│   │   ├── predict.py            # Main prediction endpoint
│   │   ├── history.py            # Prediction history
│   │   ├── health.py             # Health check
│   │   ├── subscribers.py        # Email alert subscriptions
│   │   └── site_config.py        # Admin scheduler configuration
│   ├── services/
│   │   ├── orchestrator.py       # Pipeline: fetch → model → simulate
│   │   ├── xgboost_service.py    # XGBoost inference
│   │   ├── anuga_service.py      # ANUGA hydraulic simulation
│   │   ├── api_service.py        # Open-Meteo / geocoding calls
│   │   ├── auth_service.py       # JWT + bcrypt
│   │   ├── email_service.py      # Gmail SMTP + HTML email templates
│   │   └── scheduler_service.py  # APScheduler flood-check jobs
│   ├── utils/
│   │   ├── schemas.py            # Pydantic request/response models
│   │   └── train_model.py        # Model retraining script
│   └── data/
│       └── training_data.csv     # Historical ERA5 training dataset
│
└── frontend/
    ├── vite.config.ts            # Dev server + backend proxy
    └── src/
        ├── App.tsx
        ├── store/useStore.ts     # Zustand global state
        ├── api/
        │   ├── hydroai.ts        # Core API client
        │   └── authApi.ts        # Auth + subscriber API calls
        ├── pages/
        │   ├── DashboardPage.tsx
        │   ├── LoginPage.tsx     # Parallax auth pages
        │   ├── SignupPage.tsx
        │   ├── AwarenessPage.tsx # Flood safety guide
        │   └── SiteConfigPage.tsx # Admin panel
        ├── components/
        │   ├── Header.tsx
        │   ├── FloodMap.tsx      # Leaflet map + overlays
        │   ├── Loaders.tsx       # 5 random animated CSS loaders
        │   └── SubscribeWidget.tsx
        └── styles/global.css     # CSS design token system
```

---

## API Reference

Full interactive docs at `http://localhost:8000/docs`.

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/predict` | Flood risk prediction for a location |
| `GET` | `/health` | API + model status |
| `GET` | `/history` | Paginated prediction history |
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login, returns JWT |
| `GET` | `/auth/me` | Current user profile |
| `POST` | `/subscribers/subscribe` | Subscribe to flood alerts |
| `GET` | `/subscribers/count` | Active subscriber count |
| `GET` | `/site-config` | Scheduler config (admin) |
| `PUT` | `/site-config` | Update interval / enable (admin) |
| `POST` | `/site-config/run-now` | Trigger immediate check (admin) |

---

## Alert System Flow

1. Users subscribe with their **email + city** (bell icon or Awareness page).
2. Scheduler fires at the configured interval (default: every 6 hours).
3. All locations are deduplicated — **one prediction per unique city**.
4. Each prediction pulls live ERA5 + GloFAS data for that city.
5. **High risk (score ≥ 0.6)** → styled HTML alert email sent to every subscriber in that city.
6. Low / Medium results → no email. Subscribers only hear from us when it matters.

---

## Data Sources

All free, no API key required:

| Source | Data |
|--------|------|
| Open-Meteo Forecast | 7-day rainfall accumulation |
| Open-Meteo Archive (ERA5) | Historical rainfall for date replay |
| Open-Meteo Flood (GloFAS v4) | River discharge (m³/s) |
| Open-Meteo Elevation | Copernicus DEM elevation |
| Nominatim / OpenStreetMap | Geocoding + reverse geocoding |

---

## Deployment

```bash
docker-compose up --build
```

Starts FastAPI backend + Nginx-served frontend. Set production secrets via your hosting provider's environment config — never commit `.env`.

---

## Academic Context

**Institution:** Sinhgad College of Engineering (SCOE), Pune  
**Program:** Bachelor of Engineering — Computer Engineering  
**Group:** 46  
**Subject:** Flood Prediction System using Hydrodynamic Model

The model is tuned for the **Pune Mutha–Mula river reach** (18.52°N, 73.86°E, ~2030 km² catchment) but works for any location covered by Open-Meteo.

---

## License

MIT — see [LICENSE](LICENSE) for details.
