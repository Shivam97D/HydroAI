"""
HydroAI – XGBoost Prediction Service

Loads the pre-trained model once at startup and provides:
  • predict_risk()  – returns risk_score + risk_level
  • build_insight() – generates a human-readable insight string
"""

import logging
import os
from functools import lru_cache
from typing import Optional

import numpy as np

from config import get_settings

logger = logging.getLogger("hydroai.xgboost_service")
settings = get_settings()

# Feature column order – MUST match training pipeline
FEATURE_COLUMNS = [
    "rainfall_24h",
    "rainfall_3d",
    "rainfall_7d",
    "elevation",
    "river_flow",
]


# ── Lazy singleton model loader ───────────────────────────────────────────────
_model = None


def load_model():
    """Load (and cache) the XGBoost model from disk."""
    global _model
    if _model is not None:
        return _model

    model_path = settings.MODEL_PATH
    if not os.path.exists(model_path):
        logger.warning(
            "Model file '%s' not found – using DummyModel for development.", model_path
        )
        _model = _DummyModel()
        return _model

    try:
        import joblib
        _model = joblib.load(model_path)
        logger.info("✅  XGBoost model loaded from '%s'", model_path)
    except Exception as exc:
        logger.error("Failed to load model: %s – falling back to DummyModel", exc)
        _model = _DummyModel()

    return _model


def is_model_loaded() -> bool:
    return _model is not None and not isinstance(_model, _DummyModel)


# ── Risk classification ───────────────────────────────────────────────────────
def classify_risk(score: float) -> str:
    if score < settings.LOW_RISK_THRESHOLD:
        return "Low"
    if score < settings.HIGH_RISK_THRESHOLD:
        return "Medium"
    return "High"


# ── Prediction entry point ────────────────────────────────────────────────────
def predict_risk(features: dict[str, float]) -> tuple[float, str]:
    """
    Run XGBoost inference on a feature dict.

    Returns
    -------
    (risk_score: float, risk_level: str)
    """
    model = load_model()

    # Build feature vector in correct column order
    X = np.array([[features[col] for col in FEATURE_COLUMNS]], dtype=np.float32)

    raw = model.predict_proba(X)[0][1]          # probability of flood class
    score = float(np.clip(raw, 0.0, 1.0))
    level = classify_risk(score)

    logger.info("Risk prediction: score=%.3f  level=%s", score, level)
    return score, level


# ── Human-readable insight ────────────────────────────────────────────────────
def build_insight(features: dict[str, float], risk_score: float, risk_level: str) -> str:
    parts: list[str] = []

    rf24 = features["rainfall_24h"]
    rf7d = features["rainfall_7d"]
    elev = features["elevation"]
    flow = features["river_flow"]

    if rf24 > 50:
        parts.append("very heavy 24-hour rainfall")
    elif rf24 > 25:
        parts.append("heavy 24-hour rainfall")
    elif rf24 > 10:
        parts.append("moderate rainfall")

    if rf7d > 150:
        parts.append("prolonged weekly rainfall saturation")

    if elev < 20:
        parts.append("very low elevation terrain")
    elif elev < 50:
        parts.append("low elevation")

    if flow > 500:
        parts.append("critically high river discharge")
    elif flow > 200:
        parts.append("elevated river flow")

    cause_str = ", ".join(parts) if parts else "current environmental conditions"
    return f"{risk_level} flood risk due to {cause_str}."


# ── Dummy model (dev / CI – no .pkl required) ─────────────────────────────────
class _DummyModel:
    """
    Heuristic stand-in that produces plausible scores based on features.
    Replace with the real model.pkl in production.
    """

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        (
            rainfall_24h,
            rainfall_3d,
            rainfall_7d,
            elevation,
            river_flow,
        ) = X[0]

        score = (
            min(rainfall_24h / 100, 1) * 0.35
            + min(rainfall_7d / 200, 1) * 0.20
            + max(0, (100 - elevation) / 100) * 0.25
            + min(river_flow / 1000, 1) * 0.20
        )
        score = float(np.clip(score, 0.0, 1.0))
        return np.array([[1 - score, score]])
