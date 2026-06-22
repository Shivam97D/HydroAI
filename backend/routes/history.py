"""
HydroAI – /history route
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import PredictionRecord, get_db
from utils.schemas import HistoryRecord

router = APIRouter()


@router.get(
    "/history",
    response_model=List[HistoryRecord],
    summary="Retrieve past flood predictions",
)
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    location: Optional[str] = Query(None, description="Filter by location substring"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns paginated prediction history from the database, ordered by most recent first.

    Use `location` to filter results to a specific city or region.
    """
    stmt = select(PredictionRecord).order_by(desc(PredictionRecord.timestamp))

    if location:
        stmt = stmt.where(PredictionRecord.location.ilike(f"%{location}%"))

    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [HistoryRecord(**r.to_dict()) for r in records]
