"""Periodic flood-check scheduler.

Groups all subscribers/users by location, runs ONE prediction per unique
location, and sends flood-alert emails only when risk_level == 'High'.
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("hydroai.scheduler")

scheduler = AsyncIOScheduler(timezone="UTC")
_JOB_ID = "flood_check"


# ── Core check ────────────────────────────────────────────────────────────────

async def run_flood_checks():
    """Called by APScheduler. One prediction per unique location."""
    from database.db import AsyncSessionLocal
    from database.mongo import get_mongo_db
    from services.orchestrator import orchestrate_prediction
    from services.email_service import send_email, flood_alert_html

    logger.info("Scheduled flood check started")
    db_mongo = get_mongo_db()

    await db_mongo.site_config.update_one(
        {"_id": "main"},
        {"$set": {"last_run": datetime.now(timezone.utc)}},
        upsert=True,
    )

    # Build location → {emails} map from both users and subscribers
    location_emails: dict[str, set[str]] = {}

    async for user in db_mongo.users.find(
        {"location": {"$exists": True, "$ne": ""}}
    ):
        loc = (user.get("location") or "").strip()
        email = (user.get("email") or "").strip()
        if loc and email:
            location_emails.setdefault(loc, set()).add(email)

    async for sub in db_mongo.subscribers.find(
        {"is_active": True, "location": {"$exists": True, "$ne": ""}}
    ):
        loc = (sub.get("location") or "").strip()
        email = (sub.get("email") or "").strip()
        if loc and email:
            location_emails.setdefault(loc, set()).add(email)

    if not location_emails:
        logger.info("No subscribers with a location set — skipping")
        return

    logger.info("Checking %d unique location(s)", len(location_emails))

    async with AsyncSessionLocal() as db:
        for location, emails in location_emails.items():
            try:
                result = await orchestrate_prediction(
                    location=location, lat=None, lon=None, db=db, date=None
                )
                logger.info(
                    "%-30s  risk=%-6s  score=%.2f",
                    location, result.risk_level, result.risk_score,
                )
                if result.risk_level == "High":
                    html = flood_alert_html(
                        location=result.location,
                        risk_level=result.risk_level,
                        risk_score=result.risk_score,
                        insight=result.insight,
                    )
                    subject = f"⚠️ HydroAI Flood Alert — {result.location}"
                    for email in emails:
                        await send_email(email, subject, html)
                    logger.info(
                        "Alert emails sent to %d recipient(s) for %s",
                        len(emails), location,
                    )
            except Exception as exc:
                logger.error("Flood check failed for '%s': %s", location, exc)

    logger.info("Scheduled flood check complete")


# ── Scheduler control ─────────────────────────────────────────────────────────

def start_scheduler(interval_hours: int = 6):
    if not scheduler.running:
        scheduler.start()
    _apply_interval(interval_hours)
    logger.info("Scheduler started — interval=%dh", interval_hours)


def reschedule(interval_hours: int):
    _apply_interval(interval_hours)
    logger.info("Scheduler rescheduled — interval=%dh", interval_hours)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")


def _apply_interval(hours: int):
    scheduler.add_job(
        run_flood_checks,
        trigger=IntervalTrigger(hours=hours),
        id=_JOB_ID,
        replace_existing=True,
    )
