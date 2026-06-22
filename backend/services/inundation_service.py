"""
HydroAI – Inundation Service  (real-DEM, physics-lite)

Replaces the old synthetic Gaussian-blob "ANUGA fallback" with a genuine
terrain-driven flood model that runs in seconds on any laptop (pure
numpy/scipy — no GDAL/ANUGA install required):

  1. Fetch a real Copernicus DEM grid around the query point (Open-Meteo
     Elevation API) and cache it to disk.
  2. Compute HAND – Height Above Nearest Drainage – for every cell
     (standard hydrological flood-mapping method).
  3. Convert the river discharge (m³/s, real GloFAS value) into a flood
     stage height above the channel using the reach's return-period
     thresholds.
  4. Inundate:  depth = max(0, stage − HAND).
  5. Emit flood GeoJSON + a terrain-aware PNG map.

This keeps the same SimulationResult contract the orchestrator expects, so
the rest of the pipeline is unchanged.
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

from config import get_settings
from services.api_service import fetch_elevation_grid

logger = logging.getLogger("hydroai.inundation_service")
settings = get_settings()

MAPS_DIR = Path("maps")
MAPS_DIR.mkdir(exist_ok=True)
DEM_CACHE = Path("data/dem_cache")
DEM_CACHE.mkdir(parents=True, exist_ok=True)

GRID_SIZE = 24          # DEM grid resolution (cells per side); 576 pts = 6 API calls
HALF_SPAN_DEG = 0.055   # ±degrees around the query point (~12 km box)

# Depth classes (upper bound in metres → RGB), matching the frontend legend:
# ankle / knee / waist / chest / life-threatening.
DEPTH_CLASSES = [
    (0.25, (255, 245, 157)),   # ankle  – pale yellow
    (0.50, (255, 179,   0)),   # knee   – amber
    (1.00, (255, 109,   0)),   # waist  – deep orange
    (1.80, (211,  47,  47)),   # chest  – red
    (1e9,  (106,  27, 154)),   # life-threatening – purple
]


# ── Result container (same shape orchestrator already uses) ───────────────────
@dataclass
class SimulationResult:
    run_id: str
    max_water_depth: float
    flood_map_url: str
    geojson_url: str
    geojson_data: dict
    water_depth_grid: np.ndarray
    lat_grid: np.ndarray
    lon_grid: np.ndarray
    flooded_area_km2: float = 0.0
    flood_stage_m: float = 0.0
    overlay_url: Optional[str] = None
    # [south, west, north, east] geographic bounds of the overlay PNG
    bounds: Optional[list] = None
    risk_zone_overlay_url: Optional[str] = None  # Q2 flood potential zone (always shown, faint)


# ── Thresholds (from trained model; sane defaults if absent) ──────────────────
def _load_thresholds() -> dict:
    path = Path(settings.MODEL_PATH).parent / "thresholds.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {"warning": 350.0, "Q2": 1500.0, "Q5": 2500.0, "Q10": 3000.0, "Q25": 3800.0}


# ── Public entry point ────────────────────────────────────────────────────────
async def run_simulation(
    lat: float,
    lon: float,
    rainfall_intensity: float,      # mm/hr (kept for signature compat)
    river_flow: float,               # m³/s  (real GloFAS discharge)
    risk_score: float,
) -> SimulationResult:
    t = _load_thresholds()
    q2_discharge = t.get("Q2", 1589.0)

    # Severity amplification for extreme risk only — never inflate for viz purposes
    discharge = river_flow
    if risk_score >= settings.SEVERE_RISK_THRESHOLD:
        discharge *= 1.25
        logger.info("Severe risk – amplified discharge to %.1f m³/s", discharge)

    run_id = uuid.uuid4().hex[:10]
    logger.info("Inundation run_id=%s  Q=%.1f m³/s  Q2=%.1f m³/s", run_id, discharge, q2_discharge)

    lon_grid, lat_grid, elev = await _build_dem(lat, lon)
    return await asyncio.get_event_loop().run_in_executor(
        None, _compute_inundation, run_id, lat, lon, lon_grid, lat_grid, elev, discharge, q2_discharge
    )


# ── DEM acquisition (cached) ──────────────────────────────────────────────────
async def _build_dem(lat: float, lon: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Snap the DEM centre to a coarse (~0.02° ≈ 2 km) lattice so that slightly
    # different query coordinates (e.g. successive geocoder results) reuse the
    # same cached DEM instead of triggering a fresh elevation download.
    clat = round(lat / 0.02) * 0.02
    clon = round(lon / 0.02) * 0.02
    key = f"dem_{clat:.3f}_{clon:.3f}_{GRID_SIZE}.npz"
    cache = DEM_CACHE / key
    if cache.exists():
        d = np.load(cache)
        return d["lon"], d["lat"], d["elev"]

    lats = np.linspace(clat - HALF_SPAN_DEG, clat + HALF_SPAN_DEG, GRID_SIZE)
    lons = np.linspace(clon - HALF_SPAN_DEG, clon + HALF_SPAN_DEG, GRID_SIZE)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    flat_lat = lat_grid.ravel().tolist()
    flat_lon = lon_grid.ravel().tolist()
    try:
        elev_flat = await fetch_elevation_grid(flat_lat, flat_lon)
        elev = np.array(elev_flat, dtype=float).reshape(lon_grid.shape)
        # Only persist a REAL DEM — never cache a synthetic fallback, so the
        # real terrain is fetched once the rate-limit clears.
        np.savez_compressed(cache, lon=lon_grid, lat=lat_grid, elev=elev)
        logger.info("DEM built & cached → %s (elev %.0f–%.0f m)", cache, elev.min(), elev.max())
    except Exception as e:
        logger.warning("DEM fetch failed (%s) – using synthetic ramp (not cached)", e)
        elev = _synthetic_dem(lat_grid, lon_grid)

    return lon_grid, lat_grid, elev


# ── Core: HAND + bathtub inundation ──────────────────────────────────────────
def _compute_inundation(
    run_id, lat, lon, lon_grid, lat_grid, elev, discharge, q2_discharge=1589.0
) -> SimulationResult:
    from scipy import ndimage

    # Upsample the real (coarse) DEM with smooth interpolation so HAND grades
    # continuously and the flood can spread laterally / respond to discharge.
    # The terrain is real Copernicus data; zoom just removes the blocky grid.
    z = 3
    elev = ndimage.zoom(elev, z, order=1)
    lat_grid = ndimage.zoom(lat_grid, z, order=1)
    lon_grid = ndimage.zoom(lon_grid, z, order=1)

    hand, drainage = _hand(elev)

    def _connected_depth(stage_m: float) -> np.ndarray:
        """HAND inundation + hydraulic connectivity for a given stage height."""
        d = np.clip(stage_m - hand, 0.0, None)
        d[hand > stage_m] = 0.0
        wet = d > settings.FLOOD_DEPTH_THRESHOLD
        labels, n = ndimage.label(wet)
        if n > 0:
            ch_labels = set(np.unique(labels[drainage])) - {0}
            d[~np.isin(labels, list(ch_labels))] = 0.0
        return d

    # ── Actual flood depth at real current discharge ──────────────────────────
    stage = _flood_stage(discharge)
    depth = _connected_depth(stage)

    # ── Q2 risk zone depth (2-yr return period) — always computed ────────────
    q2_stage = _flood_stage(q2_discharge)
    q2_depth = _connected_depth(q2_stage)

    result = _build_result(run_id, lat, lon, lon_grid, lat_grid, elev, depth, stage, drainage, q2_depth)
    logger.info("run_id=%s  stage=%.2fm  Q2_stage=%.2fm  max_depth=%.2fm  area=%.2fkm²",
                run_id, stage, q2_stage, result.max_water_depth, result.flooded_area_km2)
    return result


def _hand(elev: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Height Above Nearest Drainage.

    Drainage = the valley floor, approximated as the lowest ~12 % of cells.
    For every cell, HAND = its elevation minus the elevation of the nearest
    drainage cell (Euclidean nearest, via distance transform).
    """
    from scipy import ndimage

    # Candidate valley-floor cells, then keep only the largest connected
    # component → the main river channel (not scattered low pixels).
    candidate = elev <= np.percentile(elev, 8)
    labels, n = ndimage.label(candidate)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(labels), labels, index=range(1, n + 1))
        main = int(np.argmax(sizes)) + 1
        drainage = labels == main
    else:
        drainage = candidate
    if not drainage.any():
        drainage = elev <= np.percentile(elev, 5)

    # nearest drainage cell index for every cell
    inds = ndimage.distance_transform_edt(
        ~drainage, return_distances=False, return_indices=True
    )
    nearest_elev = elev[tuple(inds)]
    hand = np.clip(elev - nearest_elev, 0.0, None)
    return hand, drainage


def _flood_stage(discharge: float) -> float:
    """
    Map river discharge (m³/s) → flood stage height above the channel (m),
    anchored to the reach's return-period thresholds.

    Below warning level the stage goes negative (no inundation); the 0.01 m
    clip means the function always returns a valid float but no cell will
    exceed the FLOOD_DEPTH_THRESHOLD (0.3 m), so the depth grid stays empty.
    """
    t = _load_thresholds()
    warn = max(t.get("warning", 350.0), 1.0)
    # Allow ratio < 1 so low-flow days produce sub-zero stage (dry channel)
    ratio = max(discharge / warn, 1e-6)
    stage = 1.0 + 2.0 * math.log10(ratio)
    return float(np.clip(stage, 0.01, 8.0))


# ── River channel extraction ──────────────────────────────────────────────────
def _extract_river_channel(lon_grid, lat_grid, elev, drainage):
    """
    Return GeoJSON features for the river channel centerline and flow arrows.

    Channel line  – sorted upstream→downstream (high elev → low elev).
    Flow arrows   – unit vectors in the downhill direction at sampled points.
    """
    rows, cols = np.where(drainage)
    if len(rows) < 3:
        return []

    elevs = elev[rows, cols]
    order = np.argsort(-elevs)          # upstream first (highest elevation)
    rows, cols = rows[order], cols[order]

    # Channel LineString (≤35 pts)
    step_line = max(1, len(rows) // 35)
    lr, lc = rows[::step_line], cols[::step_line]
    channel_coords = [
        [round(float(lon_grid[r, c]), 6), round(float(lat_grid[r, c]), 6)]
        for r, c in zip(lr, lc)
    ]

    features = []
    if len(channel_coords) >= 2:
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": channel_coords},
            "properties": {"feature_type": "river_channel"},
        })

    # Flow arrows (≤15 pts) – direction = downhill = -∇elev
    grad_y, grad_x = np.gradient(elev)          # [d/drow, d/dcol]
    # 75th-percentile gradient magnitude for normalisation
    mags = np.hypot(grad_x[drainage], grad_y[drainage])
    norm_ref = float(np.percentile(mags, 75)) if mags.size else 1.0
    norm_ref = max(norm_ref, 1e-9)

    step_arr = max(1, len(rows) // 15)
    ar, ac = rows[::step_arr], cols[::step_arr]

    for r, c in zip(ar, ac):
        dx = -float(grad_x[r, c])   # flow in +lon direction
        dy = -float(grad_y[r, c])   # flow in +lat direction
        mag = math.hypot(dx, dy)
        if mag < 1e-9:
            continue
        # angle from east, counter-clockwise (standard math convention)
        angle_deg = math.degrees(math.atan2(dy, dx))
        speed = round(min(1.0, mag / norm_ref), 3)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [round(float(lon_grid[r, c]), 6), round(float(lat_grid[r, c]), 6)],
            },
            "properties": {
                "feature_type": "flow_arrow",
                "angle_deg": round(angle_deg, 1),
                "speed": speed,
            },
        })

    return features


# ── Post-processing → GeoJSON + PNG ──────────────────────────────────────────
def _build_result(run_id, lat, lon, lon_grid, lat_grid, elev, depth, stage, drainage=None, q2_depth=None) -> SimulationResult:
    threshold = settings.FLOOD_DEPTH_THRESHOLD
    mask = depth > threshold
    max_depth = float(depth.max()) if depth.size else 0.0

    # approximate cell area (km²) for flooded-area metric
    dlat = abs(lat_grid[1, 0] - lat_grid[0, 0]) if lat_grid.shape[0] > 1 else 0.003
    dlon = abs(lon_grid[0, 1] - lon_grid[0, 0]) if lon_grid.shape[1] > 1 else 0.003
    cell_km2 = (dlat * 111.0) * (dlon * 111.0 * math.cos(math.radians(lat)))
    flooded_km2 = float(mask.sum() * cell_km2)

    # GeoJSON (flooded cells as points with depth)
    features = []
    for ly, lx, d in zip(lat_grid[mask], lon_grid[mask], depth[mask]):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(lx), float(ly)]},
            "properties": {"water_depth": round(float(d), 3)},
        })

    # River channel line + flow arrows (always emitted, even for low-flood events)
    if drainage is not None:
        features.extend(_extract_river_channel(lon_grid, lat_grid, elev, drainage))

    geojson = {
        "type": "FeatureCollection",
        "properties": {
            "max_water_depth": round(max_depth, 3),
            "flooded_area_km2": round(flooded_km2, 3),
            "flood_stage_m": round(float(stage), 3),
        },
        "features": features,
    }
    (MAPS_DIR / f"flood_{run_id}.geojson").write_text(json.dumps(geojson))

    png_path = MAPS_DIR / f"flood_{run_id}.png"
    _save_flood_map(lon_grid, lat_grid, elev, depth, lat, lon, png_path)

    south, north = float(lat_grid.min()), float(lat_grid.max())
    west, east   = float(lon_grid.min()), float(lon_grid.max())
    bounds = [south, west, north, east]

    # Depth-class raster for actual flood events (opaque coloured overlay).
    overlay_url = None
    if depth.max() > settings.FLOOD_DEPTH_THRESHOLD:
        overlay_path = MAPS_DIR / f"overlay_{run_id}.png"
        _save_depth_overlay(depth, overlay_path)
        overlay_url = f"{settings.BASE_URL}/maps/overlay_{run_id}.png"

    # Q2 risk-zone raster — single faint blue layer, cached by location so it
    # is computed only once per DEM tile and reused across predictions.
    risk_zone_url = None
    if q2_depth is not None:
        clat = round(lat / 0.02) * 0.02
        clon = round(lon / 0.02) * 0.02
        q2_key = f"q2zone_{clat:.3f}_{clon:.3f}.png"
        q2_path = MAPS_DIR / q2_key
        if not q2_path.exists():
            _save_risk_zone_overlay(q2_depth, q2_path)
        risk_zone_url = f"{settings.BASE_URL}/maps/{q2_key}"

    base = settings.BASE_URL
    return SimulationResult(
        run_id=run_id,
        max_water_depth=round(max_depth, 3),
        flood_map_url=f"{base}/maps/flood_{run_id}.png",
        geojson_url=f"{base}/maps/flood_{run_id}.geojson",
        geojson_data=geojson,
        water_depth_grid=depth.ravel(),
        lat_grid=lat_grid.ravel(),
        lon_grid=lon_grid.ravel(),
        flooded_area_km2=round(flooded_km2, 3),
        flood_stage_m=round(float(stage), 3),
        overlay_url=overlay_url,
        bounds=bounds,
        risk_zone_overlay_url=risk_zone_url,
    )


def _save_risk_zone_overlay(q2_depth: np.ndarray, out_path: Path):
    """
    Render a faint single-colour overlay showing the Q2 (2-year return period)
    flood extent — the area that COULD flood in a typical bad monsoon.
    Saved once per DEM tile and reused across all predictions for that location.
    Uses a muted steel-blue distinct from the depth-class palette.
    """
    try:
        from scipy import ndimage
        from PIL import Image

        d = ndimage.zoom(q2_depth, 4, order=1)
        d = ndimage.gaussian_filter(d, sigma=1.5)

        h, w = d.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        wet = d > settings.FLOOD_DEPTH_THRESHOLD
        # Steel blue fill — unmistakably different from the yellow/orange/red depth classes
        rgba[wet, 0] = 30
        rgba[wet, 1] = 136
        rgba[wet, 2] = 229
        rgba[wet, 3] = 90          # ~35 % opacity — clearly "potential", not current

        # Soft edge
        edge = wet & ~ndimage.binary_erosion(wet, iterations=2)
        rgba[edge, 3] = 55

        rgba = np.flipud(rgba)     # north-up for Leaflet
        Image.fromarray(rgba, mode="RGBA").save(str(out_path))
    except Exception as e:
        logger.warning("Risk zone overlay render failed (%s)", e)
        out_path.write_bytes(b"")


def _save_depth_overlay(depth: np.ndarray, out_path: Path):
    """
    Render a transparent PNG where every flooded cell is filled with its
    depth-class colour (ankle→life-threatening). This is laid over the
    Leaflet basemap/satellite as a continuous inundation layer (no dots).

    The array is upsampled & vertically flipped so the PNG is north-up and
    smooth, matching the geographic bounds returned to the frontend.
    """
    try:
        from scipy import ndimage
        from PIL import Image

        # Smooth the depth field, then upscale so class boundaries look clean.
        d = ndimage.zoom(depth, 4, order=1)
        d = ndimage.gaussian_filter(d, sigma=1.0)

        h, w = d.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)

        thr = settings.FLOOD_DEPTH_THRESHOLD
        prev = thr
        for upper, (r, g, b) in DEPTH_CLASSES:
            band = (d > prev) & (d <= upper)
            rgba[band, 0] = r
            rgba[band, 1] = g
            rgba[band, 2] = b
            rgba[band, 3] = 200          # ~0.78 opacity, semi-transparent fill
            prev = upper

        # Feather the outer edge a touch for a softer flood boundary.
        wet = d > thr
        edge = wet & ~ndimage.binary_erosion(wet, iterations=1)
        rgba[edge, 3] = 150

        # PNG row 0 must be the NORTH edge; numpy row 0 is the SOUTH edge.
        rgba = np.flipud(rgba)
        Image.fromarray(rgba, mode="RGBA").save(str(out_path))
    except Exception as e:
        logger.warning("Depth overlay render failed (%s)", e)
        out_path.write_bytes(b"")


def _save_flood_map(lon_grid, lat_grid, elev, depth, clat, clon, out_path: Path):
    """Hillshade-style terrain with a blue flood overlay graded by depth."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LightSource

        extent = [lon_grid.min(), lon_grid.max(), lat_grid.min(), lat_grid.max()]
        fig, ax = plt.subplots(figsize=(8, 8), facecolor="#0f1117")

        # terrain hillshade
        ls = LightSource(azdeg=315, altdeg=45)
        shaded = ls.hillshade(elev, vert_exag=20)
        ax.imshow(shaded, extent=extent, origin="lower", cmap="gray", alpha=0.9)
        ax.imshow(elev, extent=extent, origin="lower", cmap="terrain", alpha=0.35)

        # flood overlay
        flood = np.ma.masked_where(depth <= settings.FLOOD_DEPTH_THRESHOLD, depth)
        im = ax.imshow(flood, extent=extent, origin="lower", cmap="Blues",
                       alpha=0.8, vmin=0, vmax=max(float(depth.max()), 0.5))
        cb = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
        cb.set_label("Water depth (m)", color="white")
        cb.ax.yaxis.set_tick_params(color="white")
        plt.setp(plt.getp(cb.ax.axes, "yticklabels"), color="white")

        ax.plot(clon, clat, "o", color="#ff3860", markersize=9, label="Query point")
        ax.set_title("HydroAI – Flood Inundation (HAND on Copernicus DEM)",
                     color="white", fontsize=12)
        ax.set_xlabel("Longitude", color="white")
        ax.set_ylabel("Latitude", color="white")
        ax.tick_params(colors="white")
        ax.legend(facecolor="#1b2230", labelcolor="white", loc="upper right")
        plt.tight_layout()
        plt.savefig(str(out_path), dpi=140, facecolor=fig.get_facecolor())
        plt.close()
    except Exception as e:
        logger.warning("Map render failed (%s)", e)
        out_path.write_bytes(b"")


def _synthetic_dem(lat_grid, lon_grid) -> np.ndarray:
    """Only used if the elevation API is unreachable."""
    cy = (lat_grid.min() + lat_grid.max()) / 2
    base = 550 + 4000 * (lat_grid - cy)
    valley = -30 * np.exp(-((lon_grid - lon_grid.mean()) / 0.02) ** 2)
    return base + valley
