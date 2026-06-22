"""
HydroAI – Insight routes: river-discharge hydrograph + model metrics.

These power the dashboard's time-series chart and the "model accuracy"
panel, and surface the real validation numbers for the report.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from config import get_settings
from services.api_service import fetch_discharge_series, geocode_location

logger = logging.getLogger("hydroai.routes.insights")
router = APIRouter()
settings = get_settings()


@router.get("/hydrograph", summary="River-discharge time-series (hydrograph)")
async def hydrograph(
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    location: Optional[str] = Query(None),
    past_days: int = Query(45, ge=1, le=92),
    forecast_days: int = Query(14, ge=0, le=210),
):
    """
    Real GloFAS river discharge (m³/s) over time — past reanalysis + forecast —
    for the hydrograph chart, plus the reach's return-period danger thresholds.
    """
    if lat is None or lon is None:
        if not location:
            raise HTTPException(400, "Provide lat/lon or location.")
        lat, lon = await geocode_location(location)

    try:
        series = await fetch_discharge_series(lat, lon, past_days, forecast_days)
    except Exception as e:
        logger.exception("hydrograph failed: %s", e)
        raise HTTPException(502, "Could not fetch discharge series.")

    thresholds = {}
    tp = Path(settings.MODEL_PATH).parent / "thresholds.json"
    if tp.exists():
        thresholds = json.loads(tp.read_text())

    return {
        "latitude": lat,
        "longitude": lon,
        "unit": "m³/s",
        "time": series["time"],
        "river_discharge": series["river_discharge"],
        "thresholds": thresholds,
    }


@router.get("/metrics", summary="Model validation metrics (for the report)")
async def metrics():
    """Returns the real NSE / RMSE / R² / ROC-AUC / FAR from training."""
    mp = Path(settings.MODEL_PATH).parent / "metrics.json"
    if not mp.exists():
        raise HTTPException(404, "Metrics not found – run utils/train_model.py first.")
    return json.loads(mp.read_text())
