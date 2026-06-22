"""Send HTML emails via Gmail SMTP."""
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from config import get_settings

logger = logging.getLogger("hydroai.email")
settings = get_settings()


async def send_email(to: str, subject: str, html_body: str) -> bool:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.ALERT_FROM_NAME} <{settings.GMAIL_USER}>"
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))
    try:
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=587,
            username=settings.GMAIL_USER,
            password=settings.GMAIL_APP_PASSWORD,
            start_tls=True,
        )
        logger.info("Email sent to %s", to)
        return True
    except Exception as e:
        logger.error("Failed to send email to %s: %s", to, e)
        return False


def flood_alert_html(location: str, risk_level: str, risk_score: float, insight: str) -> str:
    color = {"High": "#DC2626", "Medium": "#D97706", "Low": "#16A34A"}.get(risk_level, "#6B7280")
    return f"""<!DOCTYPE html>
<html><body style="font-family:Inter,sans-serif;background:#F5F0E8;margin:0;padding:20px;">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
  <div style="background:#2B7A5E;padding:28px 32px;">
    <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">HydroAI Flood Alert</h1>
    <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:14px;">Real-time hydrological intelligence</p>
  </div>
  <div style="padding:32px;">
    <div style="background:#FEF2F2;border:1.5px solid {color};border-radius:10px;padding:16px 20px;margin-bottom:24px;">
      <div style="font-size:12px;font-weight:600;color:{color};text-transform:uppercase;letter-spacing:0.06em;">Risk Level</div>
      <div style="font-size:28px;font-weight:800;color:{color};margin:4px 0;">{risk_level}</div>
      <div style="font-size:14px;color:#6B7280;">Risk score: {risk_score * 100:.1f}%</div>
    </div>
    <h2 style="font-size:18px;color:#1A1A1A;margin:0 0 8px;">Location: {location}</h2>
    <p style="font-size:14px;color:#4A4A4A;line-height:1.7;margin:0 0 24px;">{insight}</p>
    <div style="background:#F5F0E8;border-radius:10px;padding:16px 20px;">
      <p style="font-size:13px;color:#6B7280;margin:0;"><strong>Safety reminder:</strong> If in a flood-prone area, move to higher ground immediately. Keep emergency kit ready. Follow local authority instructions.</p>
    </div>
  </div>
  <div style="background:#F8F5F0;padding:20px 32px;border-top:1px solid #E5DFD4;">
    <p style="font-size:12px;color:#9CA3AF;margin:0;">You are receiving this because you subscribed to HydroAI flood alerts. <a href="#" style="color:#2B7A5E;">Unsubscribe</a></p>
  </div>
</div></body></html>"""


def welcome_email_html(name: str) -> str:
    return f"""<!DOCTYPE html>
<html><body style="font-family:Inter,sans-serif;background:#F5F0E8;margin:0;padding:20px;">
<div style="max-width:600px;margin:0 auto;background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
  <div style="background:#2B7A5E;padding:28px 32px;">
    <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">Welcome to HydroAI Alerts</h1>
  </div>
  <div style="padding:32px;">
    <p style="font-size:16px;color:#1A1A1A;">Hi {name},</p>
    <p style="font-size:14px;color:#4A4A4A;line-height:1.7;">You've successfully subscribed to HydroAI flood alerts. You'll receive real-time notifications when flood risk is detected in your area.</p>
    <div style="background:#F0FDF4;border-left:4px solid #16A34A;padding:16px 20px;border-radius:0 10px 10px 0;margin:24px 0;">
      <p style="font-size:13px;color:#166534;margin:0;"><strong>What to expect:</strong> We analyse live ERA5 rainfall data and GloFAS river discharge every time a prediction runs. You'll be alerted for High risk events.</p>
    </div>
    <p style="font-size:14px;color:#6B7280;">Stay safe,<br/><strong>The HydroAI Team</strong></p>
  </div>
</div></body></html>"""
