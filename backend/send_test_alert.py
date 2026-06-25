#!/usr/bin/env python3
"""One-shot script: send a demo flood alert email to shivam1771dahifale@gmail.com"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from services.email_service import send_email, flood_alert_html

RECIPIENT = "shivam1771dahifale@gmail.com"
LOCATION  = "Pune (Mutha–Mula Reach)"
RISK_LEVEL= "High"
RISK_SCORE= 0.87

INSIGHT = (
    "HydroAI has detected a HIGH flood risk for Pune based on live ERA5 rainfall "
    "and GloFAS river discharge data. Rainfall of 94.2 mm in the past 24 hours and "
    "198.7 mm over 3 days has raised river discharge to an estimated 1,920 m³/s — "
    "well above the flood danger threshold. ANUGA hydrodynamic simulation projects "
    "maximum inundation depth of 2.6 m in low-lying areas including Kasba Peth and "
    "Shivajinagar. This is a demonstration alert generated for project testing."
)

SUBJECT = "⚠️ HydroAI Flood Alert — HIGH RISK — Pune (Demo)"

async def main():
    print(f"Sending demo flood alert to {RECIPIENT} …")
    html = flood_alert_html(LOCATION, RISK_LEVEL, RISK_SCORE, INSIGHT)
    ok   = await send_email(RECIPIENT, SUBJECT, html)
    if ok:
        print("✅  Email delivered successfully!")
    else:
        print("❌  Delivery failed — check GMAIL_APP_PASSWORD in .env")

asyncio.run(main())
