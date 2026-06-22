"""
HydroAI - Flood Prediction Platform Backend
Main FastAPI Application
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.db import init_db
from database.mongo import get_mongo_client
from routes import predict, history, health, insights, auth, subscribers, site_config
from services.xgboost_service import load_model
from services.scheduler_service import start_scheduler, stop_scheduler

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("hydroai")


# ── Lifespan (startup / shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀  HydroAI backend starting …")
    await init_db()
    logger.info("✅  Database initialised")
    load_model()  # warm the flood-risk model so /health reports correctly
    logger.info("✅  Flood-risk model ready")
    try:
        mongo_client = get_mongo_client()
        await mongo_client.admin.command("ping")
        logger.info("✅  MongoDB connected")
        # Load saved interval from site_config
        from database.mongo import get_mongo_db
        db_mongo = get_mongo_db()
        cfg = await db_mongo.site_config.find_one({"_id": "main"})
        interval_hours = cfg.get("check_interval_hours", 6) if cfg else 6
        alerts_enabled = cfg.get("alerts_enabled", True) if cfg else True
        if alerts_enabled:
            start_scheduler(interval_hours)
            logger.info("✅  Flood-check scheduler started (%dh interval)", interval_hours)
    except Exception as e:
        logger.warning("⚠️  MongoDB not connected (auth/subscribers/scheduler disabled): %s", e)
    yield
    stop_scheduler()
    logger.info("🛑  HydroAI backend shutting down")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(
        title="HydroAI – Flood Prediction API",
        description=(
            "Production-ready REST API that combines XGBoost flood-risk prediction "
            "with ANUGA hydraulic simulation to deliver real-time, map-ready flood data."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS (allow the React frontend) ──────────────────────────────────────
    origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static files (flood maps / GeoJSON served directly) ──────────────────
    os.makedirs("maps", exist_ok=True)
    app.mount("/maps", StaticFiles(directory="maps"), name="maps")

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router, tags=["Health"])
    app.include_router(predict.router, tags=["Prediction"])
    app.include_router(history.router, tags=["History"])
    app.include_router(insights.router, tags=["Insights"])
    app.include_router(auth.router, tags=["Auth"])
    app.include_router(subscribers.router, tags=["Subscribers"])
    app.include_router(site_config.router, tags=["Site Config"])

    return app


app = create_app()
