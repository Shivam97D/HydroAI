"""
HydroAI – Prediction Orchestrator
"""

import json
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.db import PredictionRecord
from services.api_service import (
    fetch_all_features,
    fetch_features_for_date,
    geocode_location,
)
from services.xgboost_service import predict_risk, build_insight, load_model
from services.inundation_service import run_simulation
from services.geocoding_service import extract_affected_places  # noqa: F401
from utils.schemas import AffectedPlace, FeatureInputs, PredictResponse

logger = logging.getLogger("hydroai.orchestrator")
settings = get_settings()


async def orchestrate_prediction(
    location: Optional[str],
    lat: Optional[float],
    lon: Optional[float],
    db: AsyncSession,
    date: Optional[str] = None,
) -> PredictResponse:

    # ── 1. Resolve coordinates ─────────────────────────────────────────────────
    # If lat/lon provided directly, skip geocoding entirely
    if lat is not None and lon is not None:
        resolved_location = location or f"{lat:.4f},{lon:.4f}"
        logger.info("Using provided coordinates: (%.4f, %.4f)", lat, lon)
    else:
        # Try geocoding, with a clear error if it fails
        try:
            lat, lon = await geocode_location(location)
            resolved_location = location or f"{lat:.4f},{lon:.4f}"
        except Exception as e:
            logger.error("Geocoding failed for '%s': %s", location, e)
            raise ValueError(
                f"Could not find location '{location}'. "
                "Please provide lat/lon directly instead."
            )

    logger.info("Prediction for '%s' → (%.4f, %.4f)", resolved_location, lat, lon)

    # Ensure model is ready
    load_model()

    # ── 2. Fetch environmental features (live, or historical for replay) ──────
    if date:
        features = await fetch_features_for_date(lat, lon, date)
        logger.info("Historical features for %s: %s", date, features)
    else:
        features = await fetch_all_features(lat, lon)
        logger.info("Live features: %s", features)

    # ── 3. XGBoost inference ───────────────────────────────────────────────────
    risk_score, risk_level = predict_risk(features)
    insight = build_insight(features, risk_score, risk_level)
    # Track whether this is an actual high-risk event (used in response for UI)
    is_active_flood = risk_score >= settings.HIGH_RISK_THRESHOLD

    # ── 4. Simulation fields ───────────────────────────────────────────────────
    flood_map_url: Optional[str] = None
    geojson_url: Optional[str] = None
    max_water_depth: Optional[float] = None
    flooded_area_km2: Optional[float] = None
    flood_stage_m: Optional[float] = None
    flood_overlay_url: Optional[str] = None
    flood_bounds: Optional[List[float]] = None
    risk_zone_overlay_url: Optional[str] = None
    affected_places: List[AffectedPlace] = []

    # ── 5. Inundation – always run to show flood-prone zone on the map ────────
    # For low-risk queries the HAND model uses the actual discharge, but the
    # minimum is clamped to 80 % of the reach warning level so the riverbank
    # flood corridor is always visible ("areas that COULD flood").
    # For active floods the real discharge drives the full inundation extent.
    if True:
        logger.info("Running inundation (risk=%.3f, active_flood=%s)", risk_score, is_active_flood)
        rainfall_intensity = features["rainfall_24h"] / 24.0

        sim = await run_simulation(
            lat=lat,
            lon=lon,
            rainfall_intensity=rainfall_intensity,
            river_flow=features["river_flow"],
            risk_score=risk_score,
        )

        flood_map_url = sim.flood_map_url
        geojson_url = sim.geojson_url
        max_water_depth = sim.max_water_depth
        flooded_area_km2 = sim.flooded_area_km2
        flood_stage_m = sim.flood_stage_m
        flood_overlay_url = sim.overlay_url
        flood_bounds = sim.bounds
        risk_zone_overlay_url = sim.risk_zone_overlay_url

        # Real neighbourhood names via reverse geocoding (few separated samples);
        # bounded by a hard timeout, falling back to coordinate zones if
        # Nominatim is slow or unreachable.
        import asyncio
        try:
            raw_places = await asyncio.wait_for(
                extract_affected_places(
                    sim.lon_grid, sim.lat_grid, sim.water_depth_grid, max_places=4
                ),
                timeout=12,
            )
        except Exception as e:
            logger.warning("Reverse geocoding failed (%s) – using zone labels", e)
            raw_places = _generate_place_names(
                resolved_location, sim.lon_grid, sim.lat_grid, sim.water_depth_grid
            )
        if not raw_places:
            raw_places = _generate_place_names(
                resolved_location, sim.lon_grid, sim.lat_grid, sim.water_depth_grid
            )
        affected_places = [AffectedPlace(**p) for p in raw_places]

    # ── 6. Persist to DB ───────────────────────────────────────────────────────
    record = PredictionRecord(
        location=resolved_location,
        latitude=lat,
        longitude=lon,
        risk_score=risk_score,
        risk_level=risk_level,
        simulation_run=str(is_active_flood).lower(),
        flood_map_url=flood_map_url,
        geojson_url=geojson_url,
        max_water_depth=max_water_depth,
        affected_places=json.dumps([p.model_dump() for p in affected_places]),
        insight=insight,
        rainfall_24h=features["rainfall_24h"],
        rainfall_3d=features["rainfall_3d"],
        rainfall_7d=features["rainfall_7d"],
        elevation=features["elevation"],
        river_flow=features["river_flow"],
    )
    db.add(record)
    await db.commit()
    logger.info("Prediction saved to DB")

    # ── 7. Build response ──────────────────────────────────────────────────────
    return PredictResponse(
        location=resolved_location,
        latitude=lat,
        longitude=lon,
        risk_score=round(risk_score, 4),
        risk_level=risk_level,
        run_simulation=is_active_flood,
        flood_map_url=flood_map_url,
        geojson_url=geojson_url,
        max_water_depth=max_water_depth,
        flooded_area_km2=flooded_area_km2,
        flood_stage_m=flood_stage_m,
        flood_overlay_url=flood_overlay_url,
        flood_bounds=flood_bounds,
        risk_zone_overlay_url=risk_zone_overlay_url,
        affected_places=affected_places,
        insight=insight,
        query_date=date,
        features=FeatureInputs(**features),
    )


def _generate_place_names(location: str, lon_grid, lat_grid, depth_grid) -> List[dict]:
    """
    Generate place names from flood grid without calling external APIs.
    Uses zone labels + coordinates so the response is always fast and reliable.
    """
    import numpy as np

    threshold = settings.FLOOD_DEPTH_THRESHOLD
    mask = depth_grid > threshold
    if not mask.any():
        return []

    depths = depth_grid[mask]
    lons = lon_grid[mask]
    lats = lat_grid[mask]

    # Pick top 8 deepest cells
    idx = np.argsort(-depths)[:8]
    results = []
    seen = set()

    zone_letters = "ABCDEFGH"
    for i, cell_idx in enumerate(idx):
        d = float(depths[cell_idx])
        # Round coords to 2 dp to group nearby points
        key = (round(float(lats[cell_idx]), 2), round(float(lons[cell_idx]), 2))
        if key in seen:
            continue
        seen.add(key)
        zone = zone_letters[len(results)] if len(results) < len(zone_letters) else str(len(results)+1)
        name = f"{location} – Zone {zone} ({float(lats[cell_idx]):.3f}N)"
        results.append({
            "name": name,
            "water_depth": round(d, 2),
            "lat": round(float(lats[cell_idx]), 6),
            "lon": round(float(lons[cell_idx]), 6),
        })
        if len(results) >= 6:
            break

    return results
