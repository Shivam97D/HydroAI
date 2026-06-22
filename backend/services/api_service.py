"""
HydroAI – External API service (REAL data)

All data comes from free, no-key Open-Meteo endpoints:

  • Rainfall   – Open-Meteo Forecast API (recent past + forecast precipitation)
  • Discharge  – Open-Meteo Flood API  (GloFAS v4 river discharge, m³/s)
  • Elevation  – Open-Meteo Elevation API (Copernicus DEM)
  • Geocoding  – Nominatim / Photon

A tiny synthetic fallback remains only so a transient network failure does not
crash the pipeline; every successful call returns genuine measured/modelled
values.  See also services/anuga_service.py (real-DEM inundation) and
utils/train_model.py (real historical training data).
"""

from __future__ import annotations

import asyncio
import logging
import math
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import httpx

from config import get_settings

logger = logging.getLogger("hydroai.api_service")
settings = get_settings()

# ── Simple TTL cache ──────────────────────────────────────────────────────────
_cache: Dict[str, tuple] = {}


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < settings.CACHE_TTL_SECONDS:
        return entry[1]
    return None


def _cache_set(key: str, value):
    _cache[key] = (time.time(), value)


# ── Geocoding ─────────────────────────────────────────────────────────────────
async def geocode_location(location: str) -> Tuple[float, float]:
    """Return (lat, lon) for a place name. Tries multiple geocoders."""
    cache_key = f"geocode:{location.lower()}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    headers = {"User-Agent": "HydroAI-FloodPlatform/1.0"}

    # Try Nominatim
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                result = (float(data[0]["lat"]), float(data[0]["lon"]))
                _cache_set(cache_key, result)
                logger.info("Geocoded '%s' via Nominatim → %s", location, result)
                return result
    except Exception as e:
        logger.warning("Nominatim failed: %s", e)

    # Try Photon (alternative geocoder, no key needed)
    try:
        url = "https://photon.komoot.io/api/"
        params = {"q": location, "limit": 1}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            features = data.get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"]
                result = (float(coords[1]), float(coords[0]))
                _cache_set(cache_key, result)
                logger.info("Geocoded '%s' via Photon → %s", location, result)
                return result
    except Exception as e:
        logger.warning("Photon failed: %s", e)

    raise ValueError(
        f"Could not geocode '{location}'. "
        "Please provide lat/lon coordinates directly in your request."
    )


# ── Rainfall (Open-Meteo Forecast API – real precipitation) ───────────────────
async def fetch_rainfall(lat: float, lon: float) -> Dict[str, float]:
    """
    Trailing antecedent rainfall ending 'now', from Open-Meteo.

    Returns rainfall_24h / rainfall_3d / rainfall_7d in millimetres, computed
    from real hourly + daily precipitation (past_days window).
    """
    cache_key = f"rain:{lat:.3f},{lon:.3f}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation",
            "daily": "precipitation_sum",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "auto",
        }
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(settings.OPENMETEO_FORECAST_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

        now = datetime.now()

        # rainfall_24h – sum the last 24 hourly values that are ≤ now
        hourly = data.get("hourly", {})
        h_times = hourly.get("time", [])
        h_precip = hourly.get("precipitation", []) or []
        past_hours = [
            p or 0.0
            for t, p in zip(h_times, h_precip)
            if _parse(t) is not None and _parse(t) <= now
        ]
        rain_24h = sum(past_hours[-24:]) if past_hours else 0.0

        # rainfall_3d / 7d – trailing daily sums ending today
        daily = data.get("daily", {})
        d_times = daily.get("time", [])
        d_precip = daily.get("precipitation_sum", []) or []
        past_days = [
            p or 0.0
            for t, p in zip(d_times, d_precip)
            if _parse(t) is not None and _parse(t).date() <= now.date()
        ]
        rain_3d = sum(past_days[-3:]) if past_days else 0.0
        rain_7d = sum(past_days[-7:]) if past_days else 0.0

        result = {
            "rainfall_24h": round(rain_24h, 2),
            "rainfall_3d": round(rain_3d, 2),
            "rainfall_7d": round(rain_7d, 2),
        }
        logger.info("Real rainfall @(%.3f,%.3f): %s", lat, lon, result)
    except Exception as e:
        logger.warning("Open-Meteo rainfall failed (%s) – using synthetic fallback", e)
        result = _synthetic_rainfall(lat, lon)

    _cache_set(cache_key, result)
    return result


# ── Elevation (Open-Meteo Elevation API – Copernicus DEM) ─────────────────────
async def fetch_elevation(lat: float, lon: float) -> float:
    cache_key = f"elev:{lat:.4f},{lon:.4f}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        params = {"latitude": lat, "longitude": lon}
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(settings.OPENMETEO_ELEVATION_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
        elevation = float(data["elevation"][0])
    except Exception as e:
        logger.warning("Elevation API failed (%s) – using fallback 50m", e)
        elevation = 50.0

    _cache_set(cache_key, elevation)
    return elevation


async def fetch_elevation_grid(
    lats: List[float], lons: List[float]
) -> List[float]:
    """
    Batch elevation lookup for a DEM grid (≤ 100 points per Open-Meteo call).
    Returns elevations in the same order as the input coordinate pairs.

    Polite to the free API: spaces requests out and retries on HTTP 429 with
    exponential backoff so a transient rate-limit doesn't fail the DEM build.
    """
    out: List[float] = []
    async with httpx.AsyncClient(timeout=30) as client:
        for i in range(0, len(lats), 100):
            chunk_lat = lats[i : i + 100]
            chunk_lon = lons[i : i + 100]
            params = {
                "latitude": ",".join(f"{v:.5f}" for v in chunk_lat),
                "longitude": ",".join(f"{v:.5f}" for v in chunk_lon),
            }
            for attempt in range(4):
                resp = await client.get(settings.OPENMETEO_ELEVATION_URL, params=params)
                if resp.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logger.warning("Elevation 429 – backing off %ss", wait)
                    await asyncio.sleep(wait)
                    continue
                resp.raise_for_status()
                out.extend(float(e) for e in resp.json()["elevation"])
                break
            else:
                raise RuntimeError("Elevation API rate-limited after retries")
            await asyncio.sleep(0.4)  # gentle spacing between chunks
    return out


# ── River discharge (Open-Meteo Flood API – GloFAS v4, REAL) ──────────────────
async def fetch_river_flow(lat: float, lon: float) -> float:
    """Current river discharge (m³/s) from GloFAS – the real model discharge."""
    cache_key = f"flow:{lat:.3f},{lon:.3f}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        series = await fetch_discharge_series(lat, lon, past_days=1, forecast_days=1)
        # latest available value (today)
        flow = next(
            (v for v in reversed(series["river_discharge"]) if v is not None), None
        )
        if flow is None:
            raise ValueError("no discharge values returned")
        flow = float(flow)
    except Exception as e:
        logger.warning("GloFAS discharge failed (%s) – estimating from rainfall", e)
        flow = await _estimate_flow_from_rainfall(lat, lon)

    _cache_set(cache_key, round(flow, 2))
    return round(flow, 2)


async def fetch_discharge_series(
    lat: float, lon: float, past_days: int = 30, forecast_days: int = 14
) -> Dict[str, list]:
    """
    River-discharge time-series (for the hydrograph): dates + m³/s.
    Real GloFAS reanalysis (past) + forecast.
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "river_discharge",
        "past_days": past_days,
        "forecast_days": forecast_days,
    }
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(settings.OPENMETEO_FLOOD_URL, params=params)
        resp.raise_for_status()
        daily = resp.json().get("daily", {})
    return {
        "time": daily.get("time", []),
        "river_discharge": daily.get("river_discharge", []),
    }


async def _estimate_flow_from_rainfall(lat: float, lon: float) -> float:
    """Rational-method fallback if GloFAS is unreachable."""
    rain_data = await fetch_rainfall(lat, lon)
    runoff_coeff = 0.55
    intensity_m_per_s = rain_data["rainfall_24h"] / (24 * 3600 * 1000)
    area_m2 = settings.CATCHMENT_AREA_KM2 * 1e6
    return max(runoff_coeff * intensity_m_per_s * area_m2, 5.0)


# ── Historical features for a specific past date (scenario / validation) ──────
async def fetch_features_for_date(lat: float, lon: float, date_str: str) -> Dict[str, float]:
    """
    Antecedent rainfall + river discharge as they REALLY were on `date_str`
    (YYYY-MM-DD).  Powers historical-event replay and model validation
    (e.g. the Aug-2019 Maharashtra flood).
    """
    from datetime import datetime as _dt, timedelta

    cache_key = f"histfeat:{lat:.3f},{lon:.3f}:{date_str}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    target = _dt.strptime(date_str, "%Y-%m-%d").date()
    start = (target - timedelta(days=7)).isoformat()
    end = target.isoformat()

    async with httpx.AsyncClient(timeout=30) as client:
        # Rainfall (ERA5 archive)
        rain = {"rainfall_24h": 0.0, "rainfall_3d": 0.0, "rainfall_7d": 0.0}
        try:
            rp = {"latitude": lat, "longitude": lon, "start_date": start,
                  "end_date": end, "daily": "precipitation_sum", "timezone": "Asia/Kolkata"}
            r = await client.get(settings.OPENMETEO_ARCHIVE_URL, params=rp)
            r.raise_for_status()
            vals = [v or 0.0 for v in r.json()["daily"]["precipitation_sum"]]
            rain = {
                "rainfall_24h": round(vals[-1], 2) if vals else 0.0,
                "rainfall_3d": round(sum(vals[-3:]), 2),
                "rainfall_7d": round(sum(vals[-7:]), 2),
            }
        except Exception as e:
            logger.warning("Archive rainfall for %s failed: %s", date_str, e)

        # Discharge (GloFAS) on the target date
        flow = 5.0
        try:
            fp = {"latitude": lat, "longitude": lon, "start_date": end,
                  "end_date": end, "daily": "river_discharge"}
            r = await client.get(settings.OPENMETEO_FLOOD_URL, params=fp)
            r.raise_for_status()
            dvals = [v for v in r.json()["daily"]["river_discharge"] if v is not None]
            if dvals:
                flow = float(dvals[-1])
        except Exception as e:
            logger.warning("Archive discharge for %s failed: %s", date_str, e)

    elevation = await fetch_elevation(lat, lon)
    feats = {**rain, "elevation": elevation, "river_flow": round(flow, 2)}
    logger.info("Historical features @%s %s: %s", date_str, (lat, lon), feats)
    _cache_set(cache_key, feats)
    return feats


# ── Fetch all features concurrently ──────────────────────────────────────────
async def fetch_all_features(lat: float, lon: float) -> Dict[str, float]:
    rain_task = asyncio.create_task(fetch_rainfall(lat, lon))
    elev_task = asyncio.create_task(fetch_elevation(lat, lon))
    flow_task = asyncio.create_task(fetch_river_flow(lat, lon))

    rain, elevation, river_flow = await asyncio.gather(rain_task, elev_task, flow_task)

    return {
        "rainfall_24h": rain["rainfall_24h"],
        "rainfall_3d": rain["rainfall_3d"],
        "rainfall_7d": rain["rainfall_7d"],
        "elevation": elevation,
        "river_flow": river_flow,
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def _parse(t: str) -> Optional[datetime]:
    """Parse Open-Meteo ISO timestamps ('YYYY-MM-DDTHH:MM' or 'YYYY-MM-DD')."""
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(t, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _synthetic_rainfall(lat: float, lon: float) -> Dict[str, float]:
    """Last-resort deterministic fallback (only used on network failure)."""
    seed = abs(math.sin(lat * 127.1 + lon * 311.7))
    base = seed * 80
    return {
        "rainfall_24h": round(base, 2),
        "rainfall_3d": round(base * 2.4, 2),
        "rainfall_7d": round(base * 4.8, 2),
    }
