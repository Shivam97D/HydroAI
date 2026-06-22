"""Admin-only site configuration endpoints."""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database.mongo import get_mongo_db
from routes.auth import get_current_user
from services.scheduler_service import reschedule, run_flood_checks, scheduler, _JOB_ID

router = APIRouter(prefix="/site-config", tags=["Site Config"])

VALID_INTERVALS = [1, 3, 6, 12, 24]


def _require_admin(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, "Admin access required")
    return current_user


class SiteConfigUpdate(BaseModel):
    check_interval_hours: int
    alerts_enabled: bool


async def _get_config(db):
    doc = await db.site_config.find_one({"_id": "main"})
    if not doc:
        doc = {
            "_id": "main",
            "check_interval_hours": 6,
            "alerts_enabled": True,
            "last_run": None,
        }
        await db.site_config.insert_one(doc)
    return doc


def _next_run_iso() -> Optional[str]:
    job = scheduler.get_job(_JOB_ID)
    if job and job.next_run_time:
        return job.next_run_time.isoformat()
    return None


@router.get("")
async def get_site_config(_admin=Depends(_require_admin)):
    db = get_mongo_db()
    doc = await _get_config(db)
    return {
        "check_interval_hours": doc.get("check_interval_hours", 6),
        "alerts_enabled": doc.get("alerts_enabled", True),
        "last_run": doc.get("last_run").isoformat() if doc.get("last_run") else None,
        "next_run": _next_run_iso(),
    }


@router.put("")
async def update_site_config(body: SiteConfigUpdate, _admin=Depends(_require_admin)):
    if body.check_interval_hours not in VALID_INTERVALS:
        raise HTTPException(400, f"Interval must be one of {VALID_INTERVALS}")
    db = get_mongo_db()
    await db.site_config.update_one(
        {"_id": "main"},
        {
            "$set": {
                "check_interval_hours": body.check_interval_hours,
                "alerts_enabled": body.alerts_enabled,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )
    if body.alerts_enabled:
        reschedule(body.check_interval_hours)
    else:
        job = scheduler.get_job(_JOB_ID)
        if job:
            scheduler.remove_job(_JOB_ID)
    return {"ok": True, "next_run": _next_run_iso()}


@router.post("/run-now")
async def trigger_now(_admin=Depends(_require_admin)):
    """Manually fire a flood check immediately."""
    import asyncio
    asyncio.create_task(run_flood_checks())
    return {"ok": True, "triggered_at": datetime.now(timezone.utc).isoformat()}
