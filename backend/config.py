"""
HydroAI – Application Settings
Reads from environment variables or backend/.env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./hydroai.db"

    # ── External APIs (all free, no key required) ─────────────────────────────
    # Open-Meteo family — rainfall (forecast + ERA5 archive), GloFAS discharge,
    # and Copernicus elevation. See services/api_service.py.
    OPENMETEO_FORECAST_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPENMETEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    OPENMETEO_FLOOD_URL: str = "https://flood-api.open-meteo.com/v1/flood"
    OPENMETEO_ELEVATION_URL: str = "https://api.open-meteo.com/v1/elevation"
    # Kept for backward-compat only (no longer used; replaced by Open-Meteo).
    OPENWEATHER_API_KEY: str = "unused"
    OPEN_ELEVATION_URL: str = "https://api.open-elevation.com/api/v1/lookup"

    # ── Study area: Pune Mutha–Mula reach ─────────────────────────────────────
    # The system is tuned for this reach but the same pipeline works anywhere
    # by changing these values (multi-basin adaptability).
    STUDY_AREA_NAME: str = "Pune (Mutha–Mula reach)"
    REACH_CENTER_LAT: float = 18.5204
    REACH_CENTER_LON: float = 73.8567
    # Bounding box of the reach (used for the inundation DEM grid).
    REACH_MIN_LAT: float = 18.44
    REACH_MAX_LAT: float = 18.60
    REACH_MIN_LON: float = 73.78
    REACH_MAX_LON: float = 73.94
    # Representative catchment area upstream of the reach (km²) — Mutha at Pune.
    CATCHMENT_AREA_KM2: float = 2030.0

    # ── App ───────────────────────────────────────────────────────────────────
    BASE_URL: str = "http://localhost:8000"
    APP_ENV: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ── Model ─────────────────────────────────────────────────────────────────
    MODEL_PATH: str = "models/model.pkl"

    # ── Risk thresholds ───────────────────────────────────────────────────────
    LOW_RISK_THRESHOLD: float = 0.3
    HIGH_RISK_THRESHOLD: float = 0.6
    SEVERE_RISK_THRESHOLD: float = 0.8
    FLOOD_DEPTH_THRESHOLD: float = 0.3

    # ── Cache ─────────────────────────────────────────────────────────────────
    CACHE_TTL_SECONDS: int = 300

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI: str = "mongodb+srv://YOUR_USER:YOUR_PASS@cluster0.xxxxx.mongodb.net/hydroai?retryWrites=true&w=majority"
    MONGO_DB_NAME: str = "hydroai"

    # ── JWT Auth ──────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-this-to-a-random-64-char-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # ── Gmail SMTP (for alerts) ───────────────────────────────────────────────
    GMAIL_USER: str = "your_gmail@gmail.com"
    GMAIL_APP_PASSWORD: str = "xxxx xxxx xxxx xxxx"
    ALERT_FROM_NAME: str = "HydroAI Flood Alerts"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
