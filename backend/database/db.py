"""
HydroAI – Async SQLAlchemy database layer
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Column, DateTime, Float, Integer, String, Text, text
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

logger = logging.getLogger("hydroai.db")
settings = get_settings()

# ── Engine & session factory ──────────────────────────────────────────────────
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")
_engine_kwargs = {"echo": (settings.APP_ENV == "development"), "pool_pre_ping": not _is_sqlite}
if not _is_sqlite:
    _engine_kwargs.update({"pool_size": 10, "max_overflow": 20})

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# ── ORM Base ──────────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ── Models ────────────────────────────────────────────────────────────────────
class PredictionRecord(Base):
    """Persisted record of every flood prediction request."""

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(255), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)        # Low / Medium / High
    simulation_run = Column(String(5), nullable=False, default="false")
    flood_map_url = Column(String(512), nullable=True)
    geojson_url = Column(String(512), nullable=True)
    max_water_depth = Column(Float, nullable=True)
    affected_places = Column(Text, nullable=True)          # JSON string
    insight = Column(Text, nullable=True)

    # ── Raw feature snapshot (for audit / retraining) ─────────────────────────
    rainfall_24h = Column(Float, nullable=True)
    rainfall_3d = Column(Float, nullable=True)
    rainfall_7d = Column(Float, nullable=True)
    elevation = Column(Float, nullable=True)
    river_flow = Column(Float, nullable=True)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "simulation_run": self.simulation_run == "true",
            "flood_map_url": self.flood_map_url,
            "geojson_url": self.geojson_url,
            "max_water_depth": self.max_water_depth,
            "affected_places": json.loads(self.affected_places) if self.affected_places else [],
            "insight": self.insight,
        }


# ── Initialise (create tables) ────────────────────────────────────────────────
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ensured")


# ── Dependency: get session ───────────────────────────────────────────────────
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
