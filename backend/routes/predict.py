"""
HydroAI – /predict route
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from services.orchestrator import orchestrate_prediction
from utils.schemas import PredictRequest, PredictResponse

logger = logging.getLogger("hydroai.routes.predict")
router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Run flood risk prediction (+ optional ANUGA simulation)",
    response_description="Flood risk score, simulation output, and map URLs",
)
async def predict(
    body: PredictRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    ### Flood Risk Prediction

    **Stage 1** – Fetches live rainfall, elevation, and river-flow data.

    **Stage 2** – Runs the pre-trained XGBoost model to produce a risk score.

    **Stage 3** – If `risk_score ≥ 0.6`, triggers an ANUGA hydraulic simulation
    and returns flood maps + affected place names.

    #### Risk levels
    | Score | Level |
    |-------|-------|
    | 0–0.3 | Low |
    | 0.3–0.6 | Medium |
    | 0.6–1.0 | High |
    """
    try:
        response = await orchestrate_prediction(
            location=body.location,
            lat=body.lat,
            lon=body.lon,
            db=db,
            date=body.date,
        )
        return response
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.exception("Unhandled error in /predict: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error – check server logs.",
        )
