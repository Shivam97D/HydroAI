"""
HydroAI – Pydantic request / response schemas
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


# ── Request ───────────────────────────────────────────────────────────────────
class PredictRequest(BaseModel):
    location: Optional[str] = Field(
        None, description="City or place name"
    )
    lat: Optional[float] = Field(
        None, ge=-90, le=90, description="Latitude (optional – overrides geocoding)"
    )
    lon: Optional[float] = Field(
        None, ge=-180, le=180, description="Longitude (optional – overrides geocoding)"
    )
    date: Optional[str] = Field(
        None,
        description="Optional past date (YYYY-MM-DD) to replay a real historical "
                    "event using that day's actual rainfall & discharge.",
    )

    @model_validator(mode="after")
    def require_location_or_coords(self) -> "PredictRequest":
        if not self.location and (self.lat is None or self.lon is None):
            raise ValueError("Provide either 'location' or both 'lat' and 'lon'.")
        return self


# ── Nested schemas ────────────────────────────────────────────────────────────
class AffectedPlace(BaseModel):
    name: str
    water_depth: float = Field(..., description="Max water depth in metres")
    lat: Optional[float] = Field(None, description="Latitude of the affected cell")
    lon: Optional[float] = Field(None, description="Longitude of the affected cell")


class FeatureInputs(BaseModel):
    """Raw environmental features used by the XGBoost model."""
    rainfall_24h: float
    rainfall_3d: float
    rainfall_7d: float
    elevation: float
    river_flow: float


# ── Responses ─────────────────────────────────────────────────────────────────
class PredictResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    risk_score: float = Field(..., ge=0, le=1)
    risk_level: str = Field(..., description="Low | Medium | High")
    run_simulation: bool
    flood_map_url: Optional[str] = None
    geojson_url: Optional[str] = None
    max_water_depth: Optional[float] = None
    flooded_area_km2: Optional[float] = None
    flood_stage_m: Optional[float] = None
    flood_overlay_url: Optional[str] = None
    flood_bounds: Optional[List[float]] = None  # [south, west, north, east]
    risk_zone_overlay_url: Optional[str] = None  # Q2 flood potential (always present, faint)
    affected_places: List[AffectedPlace] = []
    insight: str
    query_date: Optional[str] = None
    features: FeatureInputs


class HistoryRecord(BaseModel):
    id: int
    location: str
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: str
    risk_score: float
    risk_level: str
    simulation_run: bool
    flood_map_url: Optional[str]
    geojson_url: Optional[str]
    max_water_depth: Optional[float]
    affected_places: List[AffectedPlace]
    insight: Optional[str]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    database: str
    version: str
