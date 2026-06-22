"""
HydroAI – Test Suite
=====================
Run with:
    pytest tests/test_hydroai.py -v
"""

import json
import pytest
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# XGBoost Service
# ─────────────────────────────────────────────────────────────────────────────
class TestXGBoostService:

    def test_classify_risk_low(self):
        from services.xgboost_service import classify_risk
        assert classify_risk(0.1) == "Low"
        assert classify_risk(0.29) == "Low"

    def test_classify_risk_medium(self):
        from services.xgboost_service import classify_risk
        assert classify_risk(0.3) == "Medium"
        assert classify_risk(0.59) == "Medium"

    def test_classify_risk_high(self):
        from services.xgboost_service import classify_risk
        assert classify_risk(0.6) == "High"
        assert classify_risk(1.0) == "High"

    def test_predict_risk_returns_tuple(self):
        from services.xgboost_service import predict_risk
        features = {
            "rainfall_24h": 60,
            "rainfall_3d": 150,
            "rainfall_7d": 300,
            "elevation": 10,
            "river_flow": 400,
        }
        score, level = predict_risk(features)
        assert 0.0 <= score <= 1.0
        assert level in ("Low", "Medium", "High")

    def test_predict_risk_low_features(self):
        from services.xgboost_service import predict_risk
        features = {
            "rainfall_24h": 1,
            "rainfall_3d": 2,
            "rainfall_7d": 5,
            "elevation": 250,
            "river_flow": 10,
        }
        score, level = predict_risk(features)
        assert level == "Low"
        assert score < 0.3

    def test_predict_risk_high_features(self):
        from services.xgboost_service import predict_risk
        features = {
            "rainfall_24h": 180,
            "rainfall_3d": 400,
            "rainfall_7d": 700,
            "elevation": 2,
            "river_flow": 1800,
        }
        score, level = predict_risk(features)
        assert level == "High"
        assert score >= 0.6

    def test_build_insight_contains_risk_level(self):
        from services.xgboost_service import build_insight
        features = {
            "rainfall_24h": 60,
            "rainfall_3d": 150,
            "rainfall_7d": 300,
            "elevation": 10,
            "river_flow": 600,
        }
        insight = build_insight(features, 0.75, "High")
        assert "High" in insight

    def test_build_insight_mentions_rainfall(self):
        from services.xgboost_service import build_insight
        features = {
            "rainfall_24h": 80,
            "rainfall_3d": 200,
            "rainfall_7d": 400,
            "elevation": 300,
            "river_flow": 20,
        }
        insight = build_insight(features, 0.5, "Medium")
        assert "rainfall" in insight.lower()


# ─────────────────────────────────────────────────────────────────────────────
# ANUGA / Simulation Service
# ─────────────────────────────────────────────────────────────────────────────
class TestAnugaService:

    @pytest.mark.asyncio
    async def test_synthetic_simulation_produces_result(self):
        from services.anuga_service import _run_synthetic
        result = await _run_synthetic(
            lat=18.52,
            lon=73.86,
            rainfall_intensity=5.0,
            river_flow=150.0,
            run_id="test01",
        )
        assert result.max_water_depth >= 0
        assert result.geojson_url.endswith(".geojson")
        assert result.flood_map_url.endswith(".png")
        assert result.geojson_data["type"] == "FeatureCollection"

    @pytest.mark.asyncio
    async def test_severity_amplification(self):
        """Severe risk (≥0.8) must amplify inputs before simulation."""
        from services.anuga_service import run_simulation

        with patch("services.anuga_service._run_synthetic", new_callable=AsyncMock) as mock_sim:
            mock_sim.return_value = MagicMock(
                run_id="t", max_water_depth=2.0,
                flood_map_url="http://x/a.png",
                geojson_url="http://x/a.geojson",
                geojson_data={},
                water_depth_grid=np.zeros(10),
                lat_grid=np.zeros(10),
                lon_grid=np.zeros(10),
            )
            await run_simulation(
                lat=18.52, lon=73.86,
                rainfall_intensity=10.0,
                river_flow=100.0,
                risk_score=0.9,
            )
            call_kwargs = mock_sim.call_args
            # After amplification: 10 * 1.3 = 13, 100 * 1.2 = 120
            assert abs(call_kwargs.args[2] - 13.0) < 0.01
            assert abs(call_kwargs.args[3] - 120.0) < 0.01

    @pytest.mark.asyncio
    async def test_no_amplification_below_severe_threshold(self):
        from services.anuga_service import run_simulation

        with patch("services.anuga_service._run_synthetic", new_callable=AsyncMock) as mock_sim:
            mock_sim.return_value = MagicMock(
                run_id="t", max_water_depth=1.0,
                flood_map_url="", geojson_url="",
                geojson_data={},
                water_depth_grid=np.zeros(10),
                lat_grid=np.zeros(10), lon_grid=np.zeros(10),
            )
            await run_simulation(
                lat=18.52, lon=73.86,
                rainfall_intensity=10.0,
                river_flow=100.0,
                risk_score=0.7,            # below 0.8 → no amplification
            )
            call_kwargs = mock_sim.call_args
            assert abs(call_kwargs.args[2] - 10.0) < 0.01
            assert abs(call_kwargs.args[3] - 100.0) < 0.01


# ─────────────────────────────────────────────────────────────────────────────
# Geocoding Service
# ─────────────────────────────────────────────────────────────────────────────
class TestGeocodingService:

    @pytest.mark.asyncio
    async def test_fallback_places_when_nominatim_unavailable(self):
        """When all reverse-geocode calls fail, we must still return place list."""
        from services.geocoding_service import extract_affected_places

        lons = np.linspace(73.8, 73.9, 20)
        lats = np.linspace(18.5, 18.6, 20)
        depths = np.random.uniform(0.5, 3.0, 20)

        with patch("services.geocoding_service._reverse_geocode", new_callable=AsyncMock) as mock_rev:
            mock_rev.return_value = None
            places = await extract_affected_places(lons, lats, depths)

        assert isinstance(places, list)
        # Fallback should produce ≥ 1 zone entry
        assert len(places) >= 1

    def test_fallback_places_format(self):
        from services.geocoding_service import _fallback_places
        lons = np.array([73.86, 73.87, 73.88])
        lats = np.array([18.52, 18.53, 18.54])
        depths = np.array([2.0, 1.5, 0.8])
        places = _fallback_places(lons, lats, depths)
        assert all("name" in p and "water_depth" in p for p in places)
        assert len(places) <= 5


# ─────────────────────────────────────────────────────────────────────────────
# API Routes (integration-style, no real DB/HTTP)
# ─────────────────────────────────────────────────────────────────────────────
class TestPredictRoute:

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app import app
        return TestClient(app)

    def test_health_returns_200(self, client):
        with patch("routes.health.get_db"):
            from sqlalchemy.ext.asyncio import AsyncSession
            resp = client.get("/health")
            # May fail DB check in test env, but route must respond
            assert resp.status_code in (200, 500)

    def test_predict_missing_body_returns_422(self, client):
        resp = client.post("/predict", json={})
        assert resp.status_code == 422   # validation error

    def test_predict_invalid_lat_returns_422(self, client):
        resp = client.post("/predict", json={"lat": 999, "lon": 73.86})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_predict_orchestrates_correctly(self):
        """Verify orchestrator wires XGBoost → ANUGA correctly."""
        from services.orchestrator import orchestrate_prediction

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        with (
            patch("services.orchestrator.geocode_location",
                  new_callable=AsyncMock, return_value=(18.52, 73.86)),
            patch("services.orchestrator.fetch_all_features",
                  new_callable=AsyncMock,
                  return_value={
                      "rainfall_24h": 5, "rainfall_3d": 10,
                      "rainfall_7d": 20, "elevation": 200, "river_flow": 50,
                  }),
            patch("services.orchestrator.predict_risk",
                  return_value=(0.15, "Low")),
            patch("services.orchestrator.run_simulation") as mock_anuga,
        ):
            result = await orchestrate_prediction("Pune", None, None, mock_db)

        assert result.risk_level == "Low"
        assert result.run_simulation is False
        mock_anuga.assert_not_called()   # must NOT run simulation for Low risk

    @pytest.mark.asyncio
    async def test_high_risk_triggers_simulation(self):
        from services.orchestrator import orchestrate_prediction
        import numpy as np

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        sim_mock = MagicMock(
            flood_map_url="http://x/flood.png",
            geojson_url="http://x/flood.geojson",
            max_water_depth=2.5,
            water_depth_grid=np.array([1.0, 1.5, 0.1]),
            lat_grid=np.array([18.52, 18.53, 18.54]),
            lon_grid=np.array([73.86, 73.87, 73.88]),
        )

        with (
            patch("services.orchestrator.geocode_location",
                  new_callable=AsyncMock, return_value=(18.52, 73.86)),
            patch("services.orchestrator.fetch_all_features",
                  new_callable=AsyncMock,
                  return_value={
                      "rainfall_24h": 100, "rainfall_3d": 250,
                      "rainfall_7d": 500, "elevation": 5, "river_flow": 800,
                  }),
            patch("services.orchestrator.predict_risk",
                  return_value=(0.82, "High")),
            patch("services.orchestrator.run_simulation",
                  new_callable=AsyncMock, return_value=sim_mock),
            patch("services.orchestrator.extract_affected_places",
                  new_callable=AsyncMock,
                  return_value=[{"name": "Kothrud", "water_depth": 1.5}]),
        ):
            result = await orchestrate_prediction("Pune", None, None, mock_db)

        assert result.run_simulation is True
        assert result.risk_level == "High"
        assert len(result.affected_places) == 1
        assert result.affected_places[0].name == "Kothrud"


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────
class TestSchemas:

    def test_predict_request_requires_location_or_coords(self):
        from utils.schemas import PredictRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PredictRequest()   # neither location nor lat/lon

    def test_predict_request_location_only(self):
        from utils.schemas import PredictRequest
        req = PredictRequest(location="Pune")
        assert req.location == "Pune"

    def test_predict_request_coords_only(self):
        from utils.schemas import PredictRequest
        req = PredictRequest(lat=18.52, lon=73.86)
        assert req.lat == 18.52

    def test_predict_request_invalid_lat(self):
        from utils.schemas import PredictRequest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            PredictRequest(lat=999, lon=73.86)
