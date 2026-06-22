"""
HydroAI – /health route
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from services.xgboost_service import is_model_loaded
from utils.schemas import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Backend health check",
)
async def health(db: AsyncSession = Depends(get_db)):
    """Returns the operational status of the backend, model, and database."""

    # Probe DB
    db_status = "ok"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {exc}"

    return HealthResponse(
        status="ok",
        model_loaded=is_model_loaded(),
        database=db_status,
        version="1.0.0",
    )
