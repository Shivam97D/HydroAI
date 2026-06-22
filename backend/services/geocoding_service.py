"""
HydroAI – Geocoding / Reverse-geocoding Service

Two operations:
  1. forward_geocode(name)   → (lat, lon)  [delegates to api_service]
  2. extract_affected_places(lon_grid, lat_grid, depth_grid)
       → list of {"name": ..., "water_depth": ...}

Nominatim rate limit: 1 req/s (free tier).
We batch sample flooded points and deduplicate by suburb/village name.
"""

import asyncio
import logging
import time
from typing import Optional

import httpx
import numpy as np

from config import get_settings

logger = logging.getLogger("hydroai.geocoding_service")
settings = get_settings()

_NOMINATIM_BASE = "https://nominatim.openstreetmap.org/reverse"
_HEADERS = {"User-Agent": "HydroAI/1.0 (flood-prediction-platform)"}

# Simple in-process cache to avoid re-querying same coordinates
_rev_cache: dict[str, Optional[str]] = {}


async def extract_affected_places(
    lon_grid: np.ndarray,
    lat_grid: np.ndarray,
    depth_grid: np.ndarray,
    max_places: int = 15,
) -> list[dict]:
    """
    Sample the flooded cells above threshold, reverse-geocode them in batches,
    deduplicate by place name, and return the top `max_places` by depth.

    Returns
    -------
    List of {"name": str, "water_depth": float}
    """
    threshold = settings.FLOOD_DEPTH_THRESHOLD
    mask = depth_grid > threshold
    if not mask.any():
        return []

    depths_flooded = depth_grid[mask]
    lons_flooded = lon_grid[mask]
    lats_flooded = lat_grid[mask]

    # Pick a handful of *spatially separated* deep cells so we reverse-geocode
    # distinct neighbourhoods (not 40 points in the same suburb). Greedy: take
    # the deepest, then the next-deepest at least ~1.5 km away, etc.
    order = np.argsort(-depths_flooded)
    picks: list[int] = []
    min_sep = 0.015  # ≈ 1.5 km in degrees
    for i in order:
        if all(
            (lons_flooded[i] - lons_flooded[j]) ** 2
            + (lats_flooded[i] - lats_flooded[j]) ** 2 > min_sep ** 2
            for j in picks
        ):
            picks.append(int(i))
        if len(picks) >= 4:
            break

    # name → {"water_depth", "lat", "lon"} (keeps the deepest cell's coords)
    place_map: dict[str, dict] = {}

    async with httpx.AsyncClient(timeout=6, headers=_HEADERS) as client:
        for i in picks:
            lon_pt = float(lons_flooded[i])
            lat_pt = float(lats_flooded[i])
            d_pt = float(depths_flooded[i])

            cached = f"{lat_pt:.3f},{lon_pt:.3f}" in _rev_cache
            name = await _reverse_geocode(client, lat_pt, lon_pt)
            if name and name not in ("Unknown", ""):
                if name not in place_map or place_map[name]["water_depth"] < d_pt:
                    place_map[name] = {"water_depth": d_pt, "lat": lat_pt, "lon": lon_pt}

            # Nominatim free tier: 1 req/s — but no need to wait on cache hits
            if not cached:
                await asyncio.sleep(1.05)

    if not place_map:
        return _fallback_places(lons_flooded, lats_flooded, depths_flooded)

    # Sort by depth descending, cap at max_places
    sorted_places = sorted(place_map.items(), key=lambda x: -x[1]["water_depth"])
    return [
        {
            "name": n,
            "water_depth": round(v["water_depth"], 2),
            "lat": round(v["lat"], 6),
            "lon": round(v["lon"], 6),
        }
        for n, v in sorted_places[:max_places]
    ]


async def _reverse_geocode(
    client: httpx.AsyncClient,
    lat: float,
    lon: float,
) -> Optional[str]:
    """Return the suburb / village / town name for a coordinate pair."""
    cache_key = f"{lat:.3f},{lon:.3f}"
    if cache_key in _rev_cache:
        return _rev_cache[cache_key]

    try:
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 14,       # neighbourhood / suburb level
            "addressdetails": 1,
        }
        resp = await client.get(_NOMINATIM_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()

        addr = data.get("address", {})
        name = (
            addr.get("suburb")
            or addr.get("neighbourhood")
            or addr.get("village")
            or addr.get("town")
            or addr.get("city_district")
            or addr.get("city")
            or data.get("display_name", "").split(",")[0].strip()
        )
        _rev_cache[cache_key] = name or "Unknown"
        return _rev_cache[cache_key]

    except Exception as exc:
        logger.warning("Reverse geocode failed for (%.3f, %.3f): %s", lat, lon, exc)
        _rev_cache[cache_key] = None
        return None


def _fallback_places(lons, lats, depths) -> list[dict]:
    """
    When Nominatim is unavailable, generate named grid cells
    (e.g. 'Zone-A at 18.52°N 73.86°E') so the response isn't empty.
    """
    results = []
    idx = np.argsort(-depths)[:5]
    for zone_id, i in enumerate(idx, 1):
        results.append({
            "name": f"Zone-{chr(64 + zone_id)} ({lats[i]:.3f}°N {lons[i]:.3f}°E)",
            "water_depth": round(float(depths[i]), 2),
            "lat": round(float(lats[i]), 6),
            "lon": round(float(lons[i]), 6),
        })
    return results
