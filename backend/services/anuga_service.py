"""
HydroAI – ANUGA Simulation Service

Orchestrates the ANUGA hydraulic simulation:
  1. Build / download DEM for the region of interest
  2. Configure ANUGA domain (boundary conditions, rainfall, discharge)
  3. Run simulation
  4. Post-process outputs → flood GeoJSON + PNG map
  5. Return SimulationResult dataclass

When ANUGA is not installed the service falls back to a realistic
synthetic simulation so the rest of the pipeline keeps working.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from config import get_settings

logger = logging.getLogger("hydroai.anuga_service")
settings = get_settings()

MAPS_DIR = Path("maps")
MAPS_DIR.mkdir(exist_ok=True)


# ── Result container ──────────────────────────────────────────────────────────
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


# ── Public entry point ────────────────────────────────────────────────────────
async def run_simulation(
    lat: float,
    lon: float,
    rainfall_intensity: float,      # mm/hr
    river_flow: float,               # m³/s
    risk_score: float,
) -> SimulationResult:
    """
    Top-level call.  Applies severity multipliers for extreme risk,
    then delegates to the real ANUGA runner or the synthetic fallback.
    """
    # Severity amplification for risk ≥ 0.8
    if risk_score >= settings.SEVERE_RISK_THRESHOLD:
        rainfall_intensity *= 1.3
        river_flow *= 1.2
        logger.info(
            "Severe risk – amplified inputs: rainfall=%.2f mm/hr  flow=%.2f m³/s",
            rainfall_intensity,
            river_flow,
        )

    run_id = uuid.uuid4().hex[:10]
    logger.info("Starting simulation run_id=%s", run_id)

    try:
        import anuga  # noqa: F401 – check import only
        result = await _run_anuga(lat, lon, rainfall_intensity, river_flow, run_id)
    except ImportError:
        logger.warning("ANUGA not installed – running synthetic simulation")
        result = await _run_synthetic(lat, lon, rainfall_intensity, river_flow, run_id)

    logger.info(
        "Simulation complete run_id=%s  max_depth=%.2f m", run_id, result.max_water_depth
    )
    return result


# ── ANUGA simulation ──────────────────────────────────────────────────────────
async def _run_anuga(
    lat: float,
    lon: float,
    rainfall_intensity: float,
    river_flow: float,
    run_id: str,
) -> SimulationResult:
    """
    Full ANUGA simulation.
    Runs in a thread pool to avoid blocking the event loop.
    """
    import asyncio
    return await asyncio.get_event_loop().run_in_executor(
        None,
        _anuga_blocking,
        lat, lon, rainfall_intensity, river_flow, run_id,
    )


def _anuga_blocking(
    lat: float,
    lon: float,
    rainfall_intensity: float,
    river_flow: float,
    run_id: str,
) -> SimulationResult:
    import anuga

    # ── Domain extents (±0.1° bounding box around point) ─────────────────────
    delta = 0.1
    polygon = [
        [lon - delta, lat - delta],
        [lon + delta, lat - delta],
        [lon + delta, lat + delta],
        [lon - delta, lat + delta],
    ]

    # ── Build DEM (use SRTM / open elevation; here we create a synthetic ramp) ─
    dem_file = _build_synthetic_dem(lat, lon, run_id)

    domain = anuga.create_domain_from_regions(
        polygon,
        boundary_tags={
            "top": [0],
            "right": [1],
            "bottom": [2],
            "left": [3],
        },
        maximum_triangle_area=0.001,
        interior_regions=[],
    )

    domain.set_name(run_id)
    domain.set_quantity("elevation", filename=dem_file, alpha=0.99)
    domain.set_quantity("friction", 0.03)
    domain.set_quantity("stage", expression="elevation")

    # ── Boundary conditions ───────────────────────────────────────────────────
    Br = anuga.Reflective_boundary(domain)
    Bd = anuga.Dirichlet_boundary([0, 0, 0])
    domain.set_boundary({"top": Br, "right": Bd, "bottom": Bd, "left": Bd})

    # ── Rainfall operator ─────────────────────────────────────────────────────
    rainfall_m_per_s = rainfall_intensity / (1000 * 3600)
    anuga.rainfall(domain, rate=rainfall_m_per_s)

    # ── Inflow (river boundary) ───────────────────────────────────────────────
    anuga.Inflow(
        domain,
        center=(lon - delta * 0.8, lat),
        radius=0.002,
        rate=river_flow,
    )

    # ── Run for 6 simulated hours ─────────────────────────────────────────────
    for _ in domain.evolve(yieldstep=600, finaltime=21600):
        pass

    depth = domain.quantities["stage"].centroid_values - \
            domain.quantities["elevation"].centroid_values
    depth = np.maximum(depth, 0)

    x, y = domain.centroid_coordinates[:, 0], domain.centroid_coordinates[:, 1]
    result = _build_result(run_id, lat, lon, x, y, depth)
    return result


# ── Synthetic simulation (fallback) ──────────────────────────────────────────
async def _run_synthetic(
    lat: float,
    lon: float,
    rainfall_intensity: float,
    river_flow: float,
    run_id: str,
) -> SimulationResult:
    """
    Gaussian-kernel flood spread model used when ANUGA is absent.
    Produces realistic-looking outputs for development / demo.
    """
    import asyncio

    def _compute():
        grid_size = 60
        delta = 0.1
        lons = np.linspace(lon - delta, lon + delta, grid_size)
        lats = np.linspace(lat - delta, lat + delta, grid_size)
        lon_grid, lat_grid = np.meshgrid(lons, lats)

        # Flood depth = Gaussian centred on river course + random topography
        rng = np.random.default_rng(seed=int(abs(lat * 100 + lon * 100)))
        cx, cy = lon + rng.uniform(-0.03, 0.03), lat + rng.uniform(-0.03, 0.03)

        dist = np.sqrt((lon_grid - cx) ** 2 + (lat_grid - cy) ** 2)
        sigma = 0.04 + (rainfall_intensity / 200) * 0.03

        base_depth = (rainfall_intensity / 50) * np.exp(-0.5 * (dist / sigma) ** 2)
        flow_contrib = (river_flow / 300) * np.exp(-0.5 * (dist / (sigma * 1.5)) ** 2)
        noise = rng.uniform(0, 0.1, lon_grid.shape)

        depth_grid = np.clip(base_depth + flow_contrib + noise, 0, None)
        return lon_grid, lat_grid, depth_grid

    lon_grid, lat_grid, depth_grid = await asyncio.get_event_loop().run_in_executor(
        None, _compute
    )

    return _build_result(run_id, lat, lon, lon_grid.ravel(), lat_grid.ravel(), depth_grid.ravel())


# ── Post-processing helpers ───────────────────────────────────────────────────
def _build_result(
    run_id: str,
    centre_lat: float,
    centre_lon: float,
    x: np.ndarray,       # longitudes (flat)
    y: np.ndarray,       # latitudes  (flat)
    depth: np.ndarray,   # water depth (flat)
) -> SimulationResult:
    threshold = settings.FLOOD_DEPTH_THRESHOLD

    max_depth = float(depth.max())

    # ── GeoJSON flood extent ──────────────────────────────────────────────────
    features = []
    for lx, ly, d in zip(x, y, depth):
        if d > threshold:
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(lx), float(ly)],
                },
                "properties": {"water_depth": round(float(d), 3)},
            })

    geojson = {"type": "FeatureCollection", "features": features}

    geojson_path = MAPS_DIR / f"flood_{run_id}.geojson"
    geojson_path.write_text(json.dumps(geojson, indent=2))

    # ── PNG flood map ─────────────────────────────────────────────────────────
    png_path = MAPS_DIR / f"flood_{run_id}.png"
    _save_flood_map(x, y, depth, centre_lat, centre_lon, png_path)

    base = settings.BASE_URL
    return SimulationResult(
        run_id=run_id,
        max_water_depth=round(max_depth, 3),
        flood_map_url=f"{base}/maps/flood_{run_id}.png",
        geojson_url=f"{base}/maps/flood_{run_id}.geojson",
        geojson_data=geojson,
        water_depth_grid=depth,
        lat_grid=y,
        lon_grid=x,
    )


def _save_flood_map(x, y, depth, centre_lat, centre_lon, out_path: Path):
    """Render a simple matplotlib flood-depth choropleth and save as PNG."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import Normalize
        import matplotlib.cm as cm

        fig, ax = plt.subplots(figsize=(8, 8), facecolor="#1a1a2e")
        ax.set_facecolor("#16213e")

        mask = depth > settings.FLOOD_DEPTH_THRESHOLD
        if mask.sum() > 0:
            sc = ax.scatter(
                x[mask], y[mask],
                c=depth[mask],
                cmap="Blues",
                norm=Normalize(vmin=0, vmax=float(depth.max())),
                s=6,
                alpha=0.85,
                edgecolors="none",
            )
            plt.colorbar(sc, ax=ax, label="Water Depth (m)", fraction=0.03)

        ax.scatter(centre_lon, centre_lat, c="red", s=80, zorder=5, label="Query Point")
        ax.set_xlabel("Longitude", color="white")
        ax.set_ylabel("Latitude", color="white")
        ax.set_title("HydroAI – Flood Extent Map", color="white", fontsize=13)
        ax.tick_params(colors="white")
        ax.legend(facecolor="#0f3460", labelcolor="white")

        plt.tight_layout()
        plt.savefig(str(out_path), dpi=150, bbox_inches="tight")
        plt.close()
        logger.info("Flood map saved → %s", out_path)
    except ImportError:
        logger.warning("matplotlib not available – skipping PNG generation")
        out_path.write_bytes(b"")


def _build_synthetic_dem(lat: float, lon: float, run_id: str) -> str:
    """Create a minimal ASCII DEM for ANUGA when a real DEM is unavailable."""
    try:
        import anuga
        delta = 0.1
        pts = [
            [lon - delta, lat - delta, 15.0],
            [lon + delta, lat - delta, 12.0],
            [lon + delta, lat + delta, 10.0],
            [lon - delta, lat + delta, 8.0],
        ]
        dem_path = f"/tmp/dem_{run_id}.csv"
        import csv
        with open(dem_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["x", "y", "z"])
            w.writerows(pts)
        return dem_path
    except Exception:
        return ""
