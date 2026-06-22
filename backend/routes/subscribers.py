"""Subscriber endpoints: subscribe, unsubscribe, send alerts."""
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr

from database.mongo import get_mongo_db
from services.email_service import flood_alert_html, send_email, welcome_email_html

router = APIRouter(prefix="/subscribers")


class SubscribeBody(BaseModel):
    name: str
    email: EmailStr
    location: str = ""


class AlertBody(BaseModel):
    location: str
    risk_level: str
    risk_score: float
    insight: str


@router.post("/subscribe", status_code=201)
async def subscribe(body: SubscribeBody, background_tasks: BackgroundTasks):
    db = get_mongo_db()
    existing = await db.subscribers.find_one({"email": body.email.lower()})
    if existing:
        if existing.get("is_active"):
            raise HTTPException(409, "Already subscribed with this email")
        await db.subscribers.update_one(
            {"_id": existing["_id"]},
            {"$set": {"is_active": True, "name": body.name.strip()}},
        )
        return {"message": "Subscription reactivated", "email": body.email}

    doc = {
        "name": body.name.strip(),
        "email": body.email.lower(),
        "location": body.location.strip(),
        "subscribed_at": datetime.now(timezone.utc),
        "is_active": True,
    }
    await db.subscribers.insert_one(doc)
    background_tasks.add_task(
        send_email,
        body.email,
        "Welcome to HydroAI Flood Alerts 🌊",
        welcome_email_html(body.name),
    )
    return {"message": "Subscribed successfully", "email": body.email}


@router.post("/unsubscribe")
async def unsubscribe(email: str):
    db = get_mongo_db()
    result = await db.subscribers.update_one(
        {"email": email.lower()}, {"$set": {"is_active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Email not found")
    return {"message": "Unsubscribed successfully"}


@router.get("/count")
async def subscriber_count():
    db = get_mongo_db()
    count = await db.subscribers.count_documents({"is_active": True})
    return {"count": count}


@router.post("/alert/send")
async def send_flood_alert(body: AlertBody, background_tasks: BackgroundTasks):
    """Send flood alert to all active subscribers. Called for High risk predictions."""
    if body.risk_level != "High":
        return {"message": "Alert only sent for High risk", "sent": 0}
    db = get_mongo_db()
    cursor = db.subscribers.find({"is_active": True})
    sent = 0
    async for sub in cursor:
        html = flood_alert_html(body.location, body.risk_level, body.risk_score, body.insight)
        background_tasks.add_task(
            send_email,
            sub["email"],
            f"🚨 Flood Alert: {body.location} — {body.risk_level} Risk",
            html,
        )
        sent += 1
    return {"message": f"Alert queued for {sent} subscribers", "sent": sent}
