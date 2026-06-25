#!/usr/bin/env python3
"""
HydroAI Project — UML & Architecture Diagram Generator
Run from project root:
    source backend/venv/bin/activate
    python documents/diagrams/generate_diagrams.py

Generates 8 PNG files inside documents/diagrams/
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mp
from matplotlib.patches import FancyBboxPatch, Ellipse
import numpy as np

DIR = os.path.dirname(os.path.abspath(__file__))

# ── Palette ──────────────────────────────────────────────────────────────────
T,  TL  = '#2B7A5E', '#C8E6D9'
DK      = '#111827'
GR, GL  = '#6B7280', '#D1D5DB'
BG, WH  = '#F5F0E8', '#FFFFFF'
BL, BLL = '#1D4ED8', '#DBEAFE'
PU, PUL = '#6D28D9', '#EDE9FE'
RD, RDL = '#B91C1C', '#FEE2E2'
OR, ORL = '#B45309', '#FDE68A'
GN, GNL = '#166534', '#D1FAE5'

# ── Canvas ───────────────────────────────────────────────────────────────────
def setup(w, h, title=''):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis('off')
    if title:
        ax.text(w / 2, h - 0.2, title, ha='center', va='top',
                fontsize=10, fontweight='bold', color=T, zorder=10)
    return fig, ax

def save(fig, name):
    path = os.path.join(DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f'  ✓  {name}')

# ── Primitives ────────────────────────────────────────────────────────────────
def rbox(ax, x, y, w, h, txt, fc=WH, ec=T, fs=7.5, lw=1.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                 facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2))
    lines = txt.split('\n')
    for i, ln in enumerate(lines):
        ty = y + h - (i + 0.5) * h / len(lines)
        ax.text(x + w / 2, ty, ln, ha='center', va='center', fontsize=fs,
                fontweight='bold' if (bold and i == 0) else 'normal',
                color=DK, zorder=3)

def diam(ax, cx, cy, w, h, txt, fc=ORL, ec=OR, fs=7):
    pts = np.array([[cx, cy + h/2], [cx + w/2, cy],
                    [cx, cy - h/2], [cx - w/2, cy]])
    ax.add_patch(mp.Polygon(pts, closed=True, facecolor=fc, edgecolor=ec,
                            linewidth=1.5, zorder=2))
    lines = txt.split('\n')
    for i, ln in enumerate(lines):
        offset = (len(lines) / 2 - 0.5 - i) * (h / 3)
        ax.text(cx, cy + offset, ln, ha='center', va='center',
                fontsize=fs, color=DK, zorder=3)

def ell(ax, cx, cy, rw, rh, txt, fc=TL, ec=T, fs=7.5):
    ax.add_patch(Ellipse((cx, cy), rw, rh, facecolor=fc, edgecolor=ec,
                         linewidth=1.5, zorder=2))
    lines = txt.split('\n')
    for i, ln in enumerate(lines):
        offset = (len(lines) / 2 - 0.5 - i) * 0.22
        ax.text(cx, cy + offset, ln, ha='center', va='center',
                fontsize=fs, color=DK, zorder=3)

def dot(ax, cx, cy, r=0.13, fc=DK):
    ax.add_patch(plt.Circle((cx, cy), r, facecolor=fc, edgecolor=DK,
                             linewidth=1.5, zorder=4))

def enddot(ax, cx, cy, r=0.16):
    ax.add_patch(plt.Circle((cx, cy), r, facecolor=WH, edgecolor=DK,
                             linewidth=2, zorder=4))
    ax.add_patch(plt.Circle((cx, cy), r * 0.58, facecolor=DK, edgecolor='none',
                             zorder=5))

def ar(ax, x1, y1, x2, y2, txt='', c=T, lw=1.5, dash=False, fs=6.8):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=c, lw=lw,
                                linestyle='dashed' if dash else 'solid'),
                zorder=3)
    if txt:
        ang = np.arctan2(y2 - y1, x2 - x1)
        nx = -np.sin(ang) * 0.18
        ny =  np.cos(ang) * 0.18
        ax.text((x1+x2)/2 + nx, (y1+y2)/2 + ny, txt,
                ha='center', va='center', fontsize=fs, color=c, zorder=5,
                bbox=dict(boxstyle='round,pad=0.08', facecolor=BG,
                          edgecolor='none', alpha=0.9))

def ln(ax, x1, y1, x2, y2, c=GL, lw=1.0, dash=False, zorder=1):
    ax.plot([x1, x2], [y1, y2], color=c, linewidth=lw,
            linestyle='--' if dash else '-', zorder=zorder)

def txt(ax, x, y, s, fs=8, c=DK, ha='center', va='center', bold=False):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=c,
            fontweight='bold' if bold else 'normal', zorder=4)

def actor(ax, cx, y_feet, name, fs=7.5):
    hd, bh, arm, leg = 0.22, 0.38, 0.28, 0.32
    ax.add_patch(plt.Circle((cx, y_feet + leg + bh + hd), hd,
                             facecolor=WH, edgecolor=DK, linewidth=1.5, zorder=3))
    ln(ax, cx, y_feet + leg + bh, cx, y_feet + leg, c=DK, lw=1.5, zorder=3)
    ln(ax, cx - arm, y_feet + leg + bh * 0.6, cx + arm, y_feet + leg + bh * 0.6,
       c=DK, lw=1.5, zorder=3)
    ln(ax, cx, y_feet + leg, cx - arm, y_feet, c=DK, lw=1.5, zorder=3)
    ln(ax, cx, y_feet + leg, cx + arm, y_feet, c=DK, lw=1.5, zorder=3)
    ax.text(cx, y_feet - 0.18, name, ha='center', va='top',
            fontsize=fs, color=DK, zorder=3)

def lifeline(ax, x, y_top, y_bot, name, fc=TL, ec=T, fs=7):
    rbox(ax, x - 0.6, y_top - 0.38, 1.2, 0.38, name, fc=fc, ec=ec, fs=fs, bold=True)
    ax.plot([x, x], [y_top, y_bot], color=GR, lw=1,
            linestyle='--', zorder=1)

def hmsg(ax, x1, x2, y, label, c=T, fs=6.5, dash=False):
    ax.annotate('', xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle='->', color=c, lw=1.5,
                                linestyle='dashed' if dash else 'solid'),
                zorder=3)
    mx = (x1 + x2) / 2
    ax.text(mx, y + 0.12, label, ha='center', va='bottom',
            fontsize=fs, color=c, zorder=4)

# =============================================================================
# 1. ACTIVITY DIAGRAM (Swim-lanes)
# =============================================================================
def d1_activity():
    W, H = 11, 16
    fig, ax = setup(W, H, 'Activity Diagram — HydroAI Prediction Pipeline')

    # Swim-lanes (4 columns)
    lanes    = ['User', 'Backend', 'External APIs', 'ANUGA']
    lcx      = [1.375, 4.125, 7.125, 9.875]  # centre x per lane
    lbnd     = [0, 2.75, 5.5, 8.5, 11]       # x boundaries
    lane_clr = ['#C8E6D960', '#FFFFFF', '#C8E6D940', '#FEE2E260']

    for i in range(4):
        ax.add_patch(mp.Rectangle((lbnd[i], 0), lbnd[i+1] - lbnd[i], H - 1.15,
                     facecolor=lane_clr[i], edgecolor=GR, linewidth=0.8, zorder=0))
        hdr_c = T if i % 2 == 0 else BL
        ax.add_patch(mp.Rectangle((lbnd[i], H - 1.15), lbnd[i+1] - lbnd[i], 0.9,
                     facecolor=hdr_c, edgecolor=DK, linewidth=1, zorder=1))
        ax.text(lcx[i], H - 0.7, lanes[i], ha='center', va='center',
                fontsize=9, fontweight='bold', color=WH, zorder=2)
        if i > 0:
            ln(ax, lbnd[i], 0, lbnd[i], H - 1.15, c=GR, lw=1.2)

    BW, BH = 2.2, 0.52  # box width / height

    def bx(lc_idx, y, t, **kw):
        cx = lcx[lc_idx]
        rbox(ax, cx - BW/2, y, BW, BH, t, **kw)
        return (cx, y + BH/2)      # return centre

    # Start node
    dot(ax, lcx[1], 14.8)

    # 1 Enter Location — User
    c1 = bx(0, 13.9, 'Enter Location', fc=TL, ec=T)
    ar(ax, lcx[1], 14.67, lcx[0] + BW/2, 14.16, txt='')

    # 2 Geocode — Backend
    c2 = bx(1, 13.0, 'Geocode Location\n(Nominatim)', fc=BLL, ec=BL)
    ar(ax, lcx[0] + BW/2, 13.9, lcx[1] - BW/2, 13.26, txt='submit', fs=6.5)

    # 3-5 Fetch APIs — External APIs lane
    c3a = bx(2, 12.1, 'Fetch ERA5 Rainfall\n(24h / 3d / 7d)', fc=TL, ec=T)
    c3b = bx(2, 11.3, 'Fetch GloFAS\nDischarge (m³/s)', fc=TL, ec=T)
    c3c = bx(2, 10.5, 'Fetch Copernicus\nDEM Elevation (m)', fc=TL, ec=T)
    ar(ax, lcx[1] + BW/2, 13.26, lcx[2] - BW/2, 12.36, txt='lat, lon', c=BL, fs=6.2)
    ar(ax, lcx[2], 12.1, lcx[2], 11.82)
    ar(ax, lcx[2], 11.3, lcx[2], 11.02)

    # 6 XGBoost — Backend
    bx(1, 9.6, 'XGBoost\nRisk Classification', fc=PUL, ec=PU, bold=True)
    ar(ax, lcx[2] - BW/2, 10.76, lcx[1] + BW/2, 9.86, txt='feature vector', c=PU, fs=6.2)

    # 7 Decision diamond
    diam(ax, lcx[1], 8.72, 2.5, 0.7, 'risk_score\n≥ 0.6 ?')
    ar(ax, lcx[1], 9.6, lcx[1], 9.07)

    # YES → ANUGA
    bx(3, 7.82, 'Run ANUGA 2D\nSimulation (6h)', fc=RDL, ec=RD)
    bx(3, 7.02, 'Generate Flood Map\n& GeoJSON Overlay', fc=RDL, ec=RD)
    ar(ax, lcx[1] + 2.5/2, 8.72, lcx[3] - BW/2, 8.08, txt='Yes', c=RD, fs=6.5)
    ar(ax, lcx[3], 7.82, lcx[3], 7.54)

    # Save to SQLite — Backend
    bx(1, 6.25, 'Save Prediction\nto SQLite', fc=WH, ec=T)
    # NO path (left bypass around diamond)
    ax.plot([lcx[1] - 2.5/2, lcx[1] - 2.5/2, lcx[1] - BW/2],
            [8.72, 6.51, 6.51], color=OR, lw=1.5, zorder=3)
    ax.annotate('', xy=(lcx[1] - BW/2, 6.51),
                xytext=(lcx[1] - BW/2 - 0.01, 6.51),
                arrowprops=dict(arrowstyle='->', color=OR, lw=1.5), zorder=3)
    txt(ax, lcx[1] - 2.5/2 - 0.22, 8.35, 'No', fs=7, c=OR)
    # ANUGA → SQLite return
    ar(ax, lcx[3] - BW/2, 7.28, lcx[1] + BW/2, 6.51, txt='maps ready', c=RD, dash=True, fs=6.2)

    # Decision: Subscribers?
    diam(ax, lcx[1], 5.32, 2.5, 0.7, 'Subscribers\nin this area?')
    ar(ax, lcx[1], 6.25, lcx[1], 5.67)

    # YES → Send emails
    bx(1, 4.42, 'Send HTML Alert\nEmails (High risk)', fc=BLL, ec=BL)
    # right bypass for YES
    ax.plot([lcx[1] + 2.5/2, lcx[1] + 2.5/2, lcx[1] + BW/2],
            [5.32, 4.68, 4.68], color=OR, lw=1.5, zorder=3)
    ax.annotate('', xy=(lcx[1] + BW/2, 4.68),
                xytext=(lcx[1] + BW/2 + 0.01, 4.68),
                arrowprops=dict(arrowstyle='->', color=OR, lw=1.5), zorder=3)
    txt(ax, lcx[1] + 2.5/2 + 0.22, 4.95, 'Yes', fs=7, c=OR)

    # Return PredictResponse
    bx(1, 3.57, 'Return\nPredictResponse (JSON)', fc=WH, ec=T)
    ar(ax, lcx[1], 4.42, lcx[1], 4.09)
    # NO bypass from subscribers
    ax.plot([lcx[1] - 2.5/2, lcx[1] - 2.5/2, lcx[1] - BW/2],
            [5.32, 3.83, 3.83], color=OR, lw=1.5, zorder=3)
    ax.annotate('', xy=(lcx[1] - BW/2, 3.83),
                xytext=(lcx[1] - BW/2 - 0.01, 3.83),
                arrowprops=dict(arrowstyle='->', color=OR, lw=1.5), zorder=3)
    txt(ax, lcx[1] - 2.5/2 - 0.22, 4.8, 'No', fs=7, c=OR)

    # Render Dashboard — User
    bx(0, 2.72, 'Render Dashboard\n(risk card, map, charts)', fc=TL, ec=T)
    ar(ax, lcx[1] - BW/2, 3.83, lcx[0] + BW/2, 2.98, txt='JSON response')

    # End node
    enddot(ax, lcx[0], 2.25)
    ar(ax, lcx[0], 2.72, lcx[0], 2.41)

    save(fig, '01_activity_diagram.png')

# =============================================================================
# 2. USE-CASE DIAGRAM
# =============================================================================
def d2_usecase():
    W, H = 13, 10
    fig, ax = setup(W, H, 'Use-Case Diagram — HydroAI System')

    # System boundary
    ax.add_patch(FancyBboxPatch((2.6, 0.5), 8.0, 8.7, boxstyle='round,pad=0.1',
                 facecolor='#F0FDF4', edgecolor=T, linewidth=2, zorder=1))
    txt(ax, 6.6, 1.0, '« HydroAI System »', fs=9, c=T, bold=True)

    # ── Actors ──────────────────────────────────────────────────────────────
    actor(ax, 1.0, 7.1, 'Guest\nUser', fs=7.5)
    actor(ax, 1.0, 4.8, 'Registered\nUser', fs=7.5)
    actor(ax, 1.0, 2.4, 'Admin', fs=7.5)
    actor(ax, 12.2, 4.9, 'Scheduler\n(System)', fs=7.5)

    # Inheritance arrows (open triangle = generalisation)
    def generalise(ax, x_child, y_child, x_parent, y_parent):
        ax.annotate('', xy=(x_parent, y_parent), xytext=(x_child, y_child),
                    arrowprops=dict(arrowstyle='-|>', color=GR, lw=1.5), zorder=3)

    generalise(ax, 1.0, 5.82, 1.0, 7.7)   # Registered extends Guest
    generalise(ax, 1.0, 3.42, 1.0, 5.55)  # Admin extends Registered

    # ── Use-cases ────────────────────────────────────────────────────────────
    uc = {
        'Search Location':           (5.0, 8.2),
        'View Flood Prediction':     (5.0, 7.1),
        'Subscribe to Alerts':       (5.0, 6.0),
        'View Awareness Page':       (5.0, 4.9),
        'Login / Signup':            (5.0, 3.8),
        'View History':              (5.0, 2.7),
        'Configure Alert Schedule':  (8.5, 7.6),
        'Trigger Manual Check':      (8.5, 6.5),
        'Run Periodic Flood Check':  (8.5, 5.2),
        'Send Alert Emails':         (8.5, 4.0),
    }
    for name, (cx, cy) in uc.items():
        ell(ax, cx, cy, 2.6, 0.58, name, fc=TL, ec=T, fs=7)

    # ── Actor → use-case lines ───────────────────────────────────────────────
    def connect(ax, ax_x, ax_y, uc_name, offset_x=0):
        cx, cy = uc[uc_name]
        ln(ax, ax_x + 0.35, ax_y, cx - 1.3 + offset_x, cy, c=GR, lw=1, zorder=2)

    # Guest
    connect(ax, 1.0, 8.25, 'Search Location')
    connect(ax, 1.0, 8.25, 'View Flood Prediction')
    connect(ax, 1.0, 8.25, 'Subscribe to Alerts')
    connect(ax, 1.0, 8.25, 'View Awareness Page')
    # Registered User (inherits above + extra)
    connect(ax, 1.0, 5.95, 'Login / Signup')
    connect(ax, 1.0, 5.95, 'View History')
    # Admin
    connect(ax, 1.0, 3.55, 'Configure Alert Schedule')
    connect(ax, 1.0, 3.55, 'Trigger Manual Check')
    # Scheduler
    connect(ax, 11.85, 5.8, 'Run Periodic Flood Check')
    connect(ax, 11.85, 5.8, 'Send Alert Emails')

    # <<include>> arrows
    def include(ax, from_name, to_name):
        fx, fy = uc[from_name]; tx, ty = uc[to_name]
        ax.annotate('', xy=(tx - 1.3, ty), xytext=(fx + 1.3, fy),
                    arrowprops=dict(arrowstyle='->', color=GR, lw=1,
                                   linestyle='dashed'), zorder=3)
        mx, my = (fx + tx)/2, (fy + ty)/2
        ax.text(mx, my + 0.2, '<<include>>', ha='center', va='bottom',
                fontsize=6, color=GR, zorder=4)

    include(ax, 'Run Periodic Flood Check', 'Send Alert Emails')

    save(fig, '02_usecase_diagram.png')

# =============================================================================
# 3. CLASS DIAGRAM
# =============================================================================
def d3_class():
    W, H = 18, 13
    fig, ax = setup(W, H, 'Class Diagram — HydroAI Backend Services')

    def cls(x, y, name, attrs, methods, nc=TL, fc=WH):
        """Draw a 3-section UML class box."""
        fs, lh = 6.5, 0.35
        n_h = 0.42
        a_h = max(len(attrs), 1) * lh
        m_h = max(len(methods), 1) * lh
        tot = n_h + a_h + m_h

        # Name band
        ax.add_patch(FancyBboxPatch((x, y + a_h + m_h), W_cls, n_h,
                     boxstyle='round,pad=0.03', facecolor=nc, edgecolor=T,
                     linewidth=1.5, zorder=2))
        ax.text(x + W_cls/2, y + a_h + m_h + n_h/2, name, ha='center',
                va='center', fontsize=7, fontweight='bold', color=DK, zorder=3)

        # Attributes
        ax.add_patch(mp.Rectangle((x, y + m_h), W_cls, a_h,
                     facecolor=fc, edgecolor=T, linewidth=1.2, zorder=2))
        ln(ax, x, y + m_h, x + W_cls, y + m_h, c=T, lw=1.2, zorder=2)
        for i, a in enumerate(attrs):
            ay = y + m_h + a_h - (i + 0.5) * lh
            ax.text(x + 0.1, ay, a, ha='left', va='center',
                    fontsize=fs, color=DK, zorder=3, family='monospace')

        # Methods
        ax.add_patch(mp.Rectangle((x, y), W_cls, m_h,
                     facecolor='#FAFAFA', edgecolor=T, linewidth=1.2, zorder=2))
        ln(ax, x, y + m_h, x, y + m_h, c=T, lw=1.2, zorder=2)
        for i, m in enumerate(methods):
            my = y + m_h - (i + 0.5) * lh
            ax.text(x + 0.1, my, m, ha='left', va='center',
                    fontsize=fs, color=BL, zorder=3, family='monospace')

        return tot   # return total height

    W_cls = 3.2

    # Row 1: Orchestrator (centre top)
    cls(7.3, 10.2, 'Orchestrator', [], ['orchestrate_prediction()'], nc=PUL)

    # Row 2: Core Services
    cls(0.3,  7.5, 'XGBoostService',
        ['model: pkl'],
        ['load_model()', 'predict(X) → float'], nc=TL)
    cls(3.9,  7.5, 'ApiService',
        ['_cache: dict'],
        ['geocode(name)', 'fetch_rainfall(lat,lon)',
         'fetch_discharge(lat,lon)', 'fetch_elevation(lat,lon)'], nc=TL)
    cls(7.5,  7.5, 'AnugaService',
        ['settings: dict'],
        ['run_simulation(lat,lon,q)', '→ {geojson, png}'], nc=TL)
    cls(11.2, 7.5, 'SchedulerService',
        ['scheduler: AsyncIOScheduler'],
        ['start_scheduler(hours)',
         'reschedule(hours)',
         'run_flood_checks()'], nc=BLL)

    # Row 3: Auth + Email
    cls(0.3, 4.5, 'AuthService', [],
        ['hash_password(plain)',
         'verify_password(plain,hash)',
         'create_access_token(data)',
         'decode_token(token)'], nc=GNL)
    cls(4.2, 4.5, 'EmailService',
        ['gmail_user: str', 'gmail_pass: str'],
        ['send_email(to,subj,html)',
         'flood_alert_html(…)',
         'welcome_html(name)'], nc=GNL)

    # Row 3: Data models (MongoDB)
    cls(7.6, 4.5, 'User',
        ['_id: ObjectId', 'name: str', 'email: str',
         'password_hash: str', 'location: str', 'role: str'],
        [], nc='#DBEAFE')
    cls(11.2, 4.5, 'Subscriber',
        ['_id: ObjectId', 'name: str', 'email: str',
         'location: str', 'is_active: bool'],
        [], nc='#DBEAFE')
    cls(14.6, 4.5, 'SiteConfig',
        ['check_interval_hours: int',
         'alerts_enabled: bool', 'last_run: datetime'],
        [], nc='#FDE68A')

    # Row 4: SQLAlchemy ORM
    cls(0.3, 1.4, 'PredictionRecord',
        ['id: int (PK)', 'location: str', 'risk_score: float',
         'risk_level: str', 'flood_map_url: str', 'geojson_url: str'],
        ['to_dict()'], nc=ORL)
    cls(4.2, 1.4, 'PredictRequest',
        ['location: str', 'lat: float', 'lon: float', 'date: str'],
        ['validate()'], nc=ORL)
    cls(7.6, 1.4, 'PredictResponse',
        ['location: str', 'risk_score: float', 'risk_level: str',
         'affected_places: list', 'insight: str'],
        [], nc=ORL)

    # ── Association arrows (uses) ─────────────────────────────────────────────
    def uses(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=GR, lw=1.2,
                                   linestyle='dashed'), zorder=3)
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.12, '«uses»',
                ha='center', va='bottom', fontsize=5.5, color=GR, zorder=4)

    # Orchestrator → services
    # Orchestrator bottom = 10.2, centre x = 7.3 + 3.2/2 = 8.9
    orch_cx = 7.3 + W_cls/2
    uses(orch_cx, 10.2, 1.9, 7.5 + 0.42)     # → XGBoostService
    uses(orch_cx, 10.2, 5.5, 7.5 + 0.42)     # → ApiService
    uses(orch_cx, 10.2, 9.1, 7.5 + 0.42)     # → AnugaService
    uses(orch_cx, 10.2, 12.8, 7.5 + 0.42)    # → SchedulerService

    # SchedulerService → EmailService
    uses(11.2 + W_cls/2, 7.5, 4.2 + W_cls/2, 4.5 + 0.42)

    # AuthService → User
    uses(0.3 + W_cls/2, 4.5, 7.6 + W_cls/2, 4.5 + 0.7)

    save(fig, '03_class_diagram.png')

# =============================================================================
# 4. ER DIAGRAM
# =============================================================================
def d4_er():
    W, H = 16, 10
    fig, ax = setup(W, H, 'Entity–Relationship Diagram — HydroAI Data Model')

    def entity(x, y, w, h, title, fields, pk='', title_fc=TL, title_txt=T, store=''):
        """Draw a table/collection entity box."""
        row_h = 0.42
        n_h = 0.5
        tot_h = n_h + len(fields) * row_h

        # Title bar
        ax.add_patch(FancyBboxPatch((x, y + len(fields)*row_h), w, n_h,
                     boxstyle='round,pad=0.03', facecolor=title_fc,
                     edgecolor=title_txt, linewidth=1.8, zorder=2))
        ax.text(x + w/2, y + len(fields)*row_h + n_h/2, title,
                ha='center', va='center', fontsize=8, fontweight='bold',
                color=title_txt, zorder=3)
        if store:
            ax.text(x + w - 0.1, y + len(fields)*row_h + n_h/2, store,
                    ha='right', va='center', fontsize=6, color=title_txt, zorder=3)

        # Field rows
        for i, fld in enumerate(fields):
            ry = y + (len(fields) - 1 - i) * row_h
            fc_row = '#F0FFF4' if (fld.startswith('_id') or fld.startswith('id')) else WH
            ax.add_patch(mp.Rectangle((x, ry), w, row_h,
                         facecolor=fc_row, edgecolor=GL, linewidth=0.8, zorder=2))
            is_pk = fld.startswith('id') or fld.startswith('_id')
            fw = 'bold' if is_pk else 'normal'
            prefix = '[PK] ' if is_pk else '     '
            ax.text(x + 0.15, ry + row_h/2, prefix + fld,
                    ha='left', va='center', fontsize=6.5, fontweight=fw,
                    color=DK, zorder=3, family='monospace')

        # Outer border
        ax.add_patch(mp.Rectangle((x, y), w, tot_h,
                     facecolor='none', edgecolor=title_txt, linewidth=1.8, zorder=3))
        return tot_h

    # ── SQLite: predictions ────────────────────────────────────────────────────
    pred_fields = [
        'id  INTEGER  PK  AUTOINCREMENT',
        'location  VARCHAR(255)',
        'latitude  FLOAT',
        'longitude  FLOAT',
        'timestamp  DATETIME',
        'risk_score  FLOAT',
        'risk_level  VARCHAR(20)',
        'simulation_run  VARCHAR(5)',
        'flood_map_url  VARCHAR(512)',
        'geojson_url  VARCHAR(512)',
        'max_water_depth  FLOAT',
        'affected_places  TEXT (JSON)',
        'insight  TEXT',
        'rainfall_24h / 3d / 7d  FLOAT',
        'elevation / river_flow  FLOAT',
    ]
    entity(0.3, 1.8, 4.4, 0, 'predictions', pred_fields,
           title_fc=ORL, title_txt=OR, store='SQLite')

    # ── MongoDB: users ────────────────────────────────────────────────────────
    user_fields = [
        '_id  ObjectId  PK',
        'name  String',
        'email  String  (unique)',
        'password_hash  String',
        'location  String',
        'role  String  (admin|user)',
        'created_at  Date',
    ]
    entity(5.4, 4.5, 3.6, 0, 'users', user_fields,
           title_fc=BLL, title_txt=BL, store='MongoDB')

    # ── MongoDB: subscribers ───────────────────────────────────────────────────
    sub_fields = [
        '_id  ObjectId  PK',
        'name  String',
        'email  String  (unique)',
        'location  String',
        'is_active  Boolean',
        'subscribed_at  Date',
    ]
    entity(9.4, 4.5, 3.6, 0, 'subscribers', sub_fields,
           title_fc=TL, title_txt=T, store='MongoDB')

    # ── MongoDB: site_config ───────────────────────────────────────────────────
    cfg_fields = [
        '_id  "main"  (singleton)',
        'check_interval_hours  Int',
        'alerts_enabled  Boolean',
        'last_run  Date',
        'updated_at  Date',
    ]
    entity(13.0, 5.2, 2.7, 0, 'site_config', cfg_fields,
           title_fc=ORL, title_txt=OR, store='MongoDB')

    # ── Labels ────────────────────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((0.3, 0.5), 4.4, 0.6, boxstyle='round,pad=0.05',
                 facecolor=ORL, edgecolor=OR, linewidth=1, zorder=2))
    txt(ax, 2.5, 0.8, 'SQLite (via SQLAlchemy + aiosqlite)\nHolds all prediction history records',
        fs=7, c=OR)

    ax.add_patch(FancyBboxPatch((5.4, 0.5), 10.3, 0.6, boxstyle='round,pad=0.05',
                 facecolor=BLL, edgecolor=BL, linewidth=1, zorder=2))
    txt(ax, 10.55, 0.8, 'MongoDB Atlas (via Motor async driver)\nHolds users, subscribers, and scheduler config',
        fs=7, c=BL)

    # ── Relationship annotations ──────────────────────────────────────────────
    # User email ↔ Subscriber email (optional)
    x_u = 5.4 + 3.6/2; y_u = 4.5 + 7*0.42 + 0.5
    x_s = 9.4 + 3.6/2; y_s = 4.5 + 6*0.42 + 0.5
    ln(ax, x_u, y_u, x_s, y_s, c=GR, lw=1, dash=True, zorder=2)
    ax.text((x_u+x_s)/2, (y_u+y_s)/2 + 0.2,
            'email link\n(optional)', ha='center', va='bottom', fontsize=6, color=GR)

    # SchedulerService → site_config (reads)
    ax.text(13.0 + 2.7/2, 5.2 + 5*0.42 + 0.5 + 0.3,
            'read/write by\nSchedulerService', ha='center', va='bottom',
            fontsize=6, color=OR)

    save(fig, '04_er_diagram.png')

# =============================================================================
# 5. SEQUENCE DIAGRAM — Prediction Request
# =============================================================================
def d5_seq_predict():
    W, H = 18, 12
    fig, ax = setup(W, H, 'Sequence Diagram — Flood Prediction Request')

    # Lifelines
    lls = ['User', 'Browser\n/React', 'FastAPI\n/predict', 'ApiService',
           'XGBoost\nService', 'ANUGA\nService', 'SQLite', 'MongoDB\nAtlas']
    xs  = [1.1, 3.0, 5.0, 7.0, 9.0, 11.0, 13.2, 15.4]
    y_top, y_bot = 11.2, 0.5

    for x, name in zip(xs, lls):
        fc = TL if name not in ('ANUGA\nService', 'FastAPI\n/predict') else BLL
        lifeline(ax, x, y_top, y_bot, name, fc=fc, fs=6.8)

    # Alt frame for High-risk condition
    ax.add_patch(FancyBboxPatch((4.0, 4.8), 7.8, 3.4, boxstyle='round,pad=0.05',
                 facecolor='#FEF9C3', edgecolor=OR, linewidth=1.5,
                 linestyle='--', zorder=1))
    txt(ax, 4.35, 8.15, 'alt  [risk_score ≥ 0.6 — High risk]', fs=7, c=OR, ha='left')

    # ── Messages ──────────────────────────────────────────────────────────────
    msgs = [
        # (from_x, to_x, y, label, dashed, colour)
        (xs[0], xs[1], 10.7, 'Enter location + click Search', False, DK),
        (xs[1], xs[2], 10.2, 'POST /predict  {location}', False, BL),
        (xs[2], xs[3], 9.7,  'geocode_location(name)', False, T),
        (xs[3], xs[2], 9.2,  '(lat, lon)', True, GR),
        (xs[2], xs[3], 8.7,  'fetch_rainfall(lat,lon)', False, T),
        (xs[3], xs[2], 8.2,  'rainfall_24h, 3d, 7d', True, GR),
        (xs[2], xs[3], 7.7,  'fetch_discharge(lat,lon)', False, T),
        (xs[3], xs[2], 7.2,  'discharge (m³/s)', True, GR),
        # ── High-risk alt block ─────────────────────────────────────────────
        (xs[2], xs[4], 6.8,  'predict(feature_vector)', False, PU),
        (xs[4], xs[2], 6.3,  'risk_score = 0.82  →  High', True, PU),
        (xs[2], xs[5], 5.8,  'run_simulation(lat,lon,q)', False, RD),
        (xs[5], xs[2], 5.3,  'geojson_url, png_url', True, RD),
        # ── End alt block ────────────────────────────────────────────────────
        (xs[2], xs[6], 4.5,  'INSERT PredictionRecord', False, T),
        (xs[6], xs[2], 4.0,  'id = 42', True, GR),
        (xs[2], xs[7], 3.5,  'find subscribers\nfor location', False, BL),
        (xs[7], xs[2], 3.0,  '[shivam@…, janhavi@…]', True, GR),
        (xs[2], xs[1], 2.5,  'PredictResponse (JSON)', True, T),
        (xs[1], xs[0], 2.0,  'Render dashboard\n(risk card, flood map, charts)', True, DK),
    ]

    for x1, x2, y, label, dash, c in msgs:
        hmsg(ax, x1, x2, y, label, dash=dash, c=c, fs=6.5)

    # Activation bars
    for xi, ya, yb in [(xs[2], 10.2, 2.5), (xs[3], 9.7, 7.2),
                        (xs[4], 6.8, 6.3), (xs[5], 5.8, 5.3),
                        (xs[6], 4.5, 4.0), (xs[7], 3.5, 3.0)]:
        ax.add_patch(mp.Rectangle((xi - 0.12, yb), 0.24, ya - yb,
                     facecolor=WH, edgecolor=T, linewidth=1, zorder=2))

    save(fig, '05_sequence_prediction.png')

# =============================================================================
# 6. SEQUENCE DIAGRAM — Scheduler Alert Flow
# =============================================================================
def d6_seq_scheduler():
    W, H = 16, 12
    fig, ax = setup(W, H, 'Sequence Diagram — Scheduler Flood Alert Flow')

    lls = ['APScheduler', 'Scheduler\nService', 'MongoDB\nAtlas', 'Orchestrator',
           'ApiService\n+XGBoost', 'Email\nService', 'Gmail\nSMTP', 'Subscriber\nInbox']
    xs  = [1.0, 3.0, 5.2, 7.2, 9.2, 11.2, 13.2, 15.2]
    y_top, y_bot = 11.2, 0.5

    ll_colors = [ORL, TL, BLL, PUL, TL, GNL, WH, WH]
    for x, name, fc in zip(xs, lls, ll_colors):
        lifeline(ax, x, y_top, y_bot, name, fc=fc, ec=T, fs=6.5)

    msgs = [
        (xs[0], xs[1], 10.7, 'trigger() — interval elapsed', False, OR),
        (xs[1], xs[2], 10.2, 'find(users+subscribers\nwith location field)', False, BL),
        (xs[2], xs[1], 9.6,  'records with locations', True, GR),
        (xs[1], xs[1], 9.1,  'group by unique location', False, T),   # self
        (xs[1], xs[3], 8.6,  'orchestrate_prediction\n(location="Pune")', False, PU),
        (xs[3], xs[4], 8.1,  'fetch_rainfall, fetch_discharge,\nfetch_elevation', False, T),
        (xs[4], xs[3], 7.5,  'feature vector', True, GR),
        (xs[3], xs[4], 7.0,  'predict(X)', False, PU),
        (xs[4], xs[3], 6.5,  'risk_score=0.82 → High', True, PU),
        (xs[3], xs[1], 6.0,  'PredictResponse (High)', True, PU),
        (xs[1], xs[5], 5.5,  'flood_alert_html(loc, score, insight)', False, GN),
        (xs[5], xs[6], 5.0,  'SMTP send() — TLS 587', False, GN),
        (xs[6], xs[7], 4.5,  'email delivered', True, GR),
        (xs[1], xs[2], 4.0,  'update site_config.last_run', False, BL),
        (xs[2], xs[1], 3.5,  'OK', True, GR),
        (xs[1], xs[0], 3.0,  'job complete', True, T),
    ]

    for x1, x2, y, label, dash, c in msgs:
        if x1 == x2:   # self-message
            ax.annotate('', xy=(x2 + 0.3, y - 0.35), xytext=(x1, y),
                        arrowprops=dict(arrowstyle='->', color=c, lw=1.5,
                                       connectionstyle='arc3,rad=-0.5'), zorder=3)
            ax.text(x1 + 0.5, y - 0.18, label, ha='left', va='center',
                    fontsize=6.5, color=c, zorder=4)
        else:
            hmsg(ax, x1, x2, y, label, dash=dash, c=c, fs=6.3)

    # Alt frame for High-risk condition
    ax.add_patch(FancyBboxPatch((4.5, 4.8), 8.0, 3.2, boxstyle='round,pad=0.05',
                 facecolor='#FEF9C380', edgecolor=OR, linewidth=1.5,
                 linestyle='--', zorder=1))
    txt(ax, 4.85, 7.95, 'alt  [risk_level == "High"]', fs=7, c=OR, ha='left')

    # Repeat frame
    ax.add_patch(FancyBboxPatch((1.7, 5.5), 10.5, 3.5, boxstyle='round,pad=0.1',
                 facecolor='none', edgecolor=BL, linewidth=1.2,
                 linestyle='--', zorder=1))
    txt(ax, 2.0, 8.95, 'loop  [for each unique location]', fs=7, c=BL, ha='left')

    save(fig, '06_sequence_scheduler.png')

# =============================================================================
# 7. STATE MACHINE DIAGRAM — Prediction Lifecycle
# =============================================================================
def d7_state():
    W, H = 12, 11
    fig, ax = setup(W, H, 'State Machine — Prediction Lifecycle')

    SW, SH = 2.8, 0.65   # state box width / height

    states = {
        'IDLE':          (5.0, 9.8),
        'FETCHING_DATA': (5.0, 8.3),
        'CLASSIFYING':   (5.0, 6.8),
        'SIMULATING':    (8.5, 5.3),
        'SAVING':        (5.0, 5.3),
        'COMPLETE':      (5.0, 3.8),
        'ERROR':         (1.5, 5.3),
    }
    state_colors = {
        'IDLE':          (TL, T),
        'FETCHING_DATA': (BLL, BL),
        'CLASSIFYING':   (PUL, PU),
        'SIMULATING':    (RDL, RD),
        'SAVING':        (ORL, OR),
        'COMPLETE':      (GNL, GN),
        'ERROR':         (RDL, RD),
    }

    for name, (cx, cy) in states.items():
        fc, ec = state_colors[name]
        rbox(ax, cx - SW/2, cy - SH/2, SW, SH, name, fc=fc, ec=ec, fs=8, bold=True)

    # Start
    dot(ax, 6.4, 10.65, r=0.14)
    ar(ax, 6.4, 10.51, 6.4, 10.13, c=DK)
    ar(ax, 6.4, 10.13, states['IDLE'][0] + SW/2, states['IDLE'][1], c=DK)

    # IDLE → FETCHING_DATA
    ar(ax, states['IDLE'][0], states['IDLE'][1] - SH/2,
       states['FETCHING_DATA'][0], states['FETCHING_DATA'][1] + SH/2,
       txt='search submitted', c=T)

    # FETCHING_DATA → CLASSIFYING
    ar(ax, states['FETCHING_DATA'][0], states['FETCHING_DATA'][1] - SH/2,
       states['CLASSIFYING'][0], states['CLASSIFYING'][1] + SH/2,
       txt='data received', c=BL)

    # CLASSIFYING → SIMULATING (High risk)
    ar(ax, states['CLASSIFYING'][0] + SW/2, states['CLASSIFYING'][1],
       states['SIMULATING'][0] - SW/2, states['SIMULATING'][1],
       txt='risk ≥ 0.6\n(High)', c=RD)

    # CLASSIFYING → SAVING (not High)
    ar(ax, states['CLASSIFYING'][0] - SW/2, states['CLASSIFYING'][1],
       states['SAVING'][0] - SW/2 - 0.5, states['SAVING'][1],
       txt='risk < 0.6', c=OR)
    ax.annotate('', xy=(states['SAVING'][0] - SW/2, states['SAVING'][1]),
                xytext=(states['SAVING'][0] - SW/2 - 0.5, states['SAVING'][1]),
                arrowprops=dict(arrowstyle='->', color=OR, lw=1.5), zorder=3)

    # SIMULATING → SAVING
    ar(ax, states['SIMULATING'][0] - SW/2, states['SIMULATING'][1],
       states['SAVING'][0] + SW/2, states['SAVING'][1],
       txt='maps generated', c=RD)

    # SAVING → COMPLETE
    ar(ax, states['SAVING'][0], states['SAVING'][1] - SH/2,
       states['COMPLETE'][0], states['COMPLETE'][1] + SH/2,
       txt='DB write OK', c=OR)

    # COMPLETE → end state
    enddot(ax, states['COMPLETE'][0], states['COMPLETE'][1] - SH/2 - 0.35)
    ar(ax, states['COMPLETE'][0], states['COMPLETE'][1] - SH/2,
       states['COMPLETE'][0], states['COMPLETE'][1] - SH/2 - 0.2, c=GN)

    # Any state → ERROR
    for name in ['FETCHING_DATA', 'CLASSIFYING', 'SIMULATING', 'SAVING']:
        sx, sy = states[name]
        ex, ey = states['ERROR']
        ar(ax, sx - SW/2, sy, ex + SW/2, ey,
           txt='' , c=RD, lw=1, dash=True)

    txt(ax, states['ERROR'][0], states['ERROR'][1] - SH/2 - 0.25,
        '(any state → ERROR\non unhandled exception)', fs=6, c=RD)

    # Legend
    for i, (label_s, fc, ec) in enumerate([
        ('Low risk → no ANUGA', ORL, OR),
        ('High risk → ANUGA triggered', RDL, RD),
        ('Success path', GNL, GN),
        ('Error path (dashed)', RDL, RD),
    ]):
        lx, ly = 0.3, 2.5 - i * 0.55
        rbox(ax, lx, ly - 0.18, 0.7, 0.36, '', fc=fc, ec=ec, fs=6)
        txt(ax, lx + 0.85, ly, label_s, fs=6.5, ha='left', c=DK)

    save(fig, '07_state_machine.png')

# =============================================================================
# 8. DEPLOYMENT DIAGRAM
# =============================================================================
def d8_deployment():
    W, H = 15, 10
    fig, ax = setup(W, H, 'Deployment Diagram — HydroAI System')

    def node(x, y, w, h, title, components, nc=TL, tc=T):
        """Draw a UML deployment node (3D-style box)."""
        depth = 0.25
        # Top face
        ax.add_patch(mp.FancyArrowPatch((x, y + h),
                     (x + depth, y + h + depth/2),
                     arrowstyle='-', color=tc, lw=1.5))
        ax.add_patch(mp.FancyArrowPatch((x + w, y + h),
                     (x + w + depth, y + h + depth/2),
                     arrowstyle='-', color=tc, lw=1.5))
        ax.add_patch(mp.FancyArrowPatch((x, y + h),
                     (x + w, y + h),
                     arrowstyle='-', color=tc, lw=1.5))
        ax.add_patch(mp.FancyArrowPatch((x + depth, y + h + depth/2),
                     (x + w + depth, y + h + depth/2),
                     arrowstyle='-', color=tc, lw=1.5))
        # Right face
        ax.add_patch(mp.FancyArrowPatch((x + w, y),
                     (x + w + depth, y + depth/2),
                     arrowstyle='-', color=tc, lw=1.5))
        ax.add_patch(mp.FancyArrowPatch((x + w + depth, y + depth/2),
                     (x + w + depth, y + h + depth/2),
                     arrowstyle='-', color=tc, lw=1.5))

        # Main face
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.05',
                     facecolor=nc, edgecolor=tc, linewidth=2, zorder=2))

        # Title band
        ax.add_patch(mp.Rectangle((x, y + h - 0.55), w, 0.55,
                     facecolor=tc, edgecolor=tc, linewidth=0, zorder=3))
        ax.text(x + w/2, y + h - 0.28, title, ha='center', va='center',
                fontsize=8, fontweight='bold', color=WH, zorder=4)

        # Components
        for i, comp in enumerate(components):
            cy_c = y + h - 0.8 - i * 0.55
            ax.add_patch(FancyBboxPatch((x + 0.15, cy_c - 0.2), w - 0.3, 0.42,
                         boxstyle='round,pad=0.03', facecolor=WH, edgecolor=tc,
                         linewidth=1, zorder=4))
            ax.text(x + 0.25, cy_c, comp, ha='left', va='center',
                    fontsize=6.5, color=DK, zorder=5)

    # ── Nodes ─────────────────────────────────────────────────────────────────
    node(0.3, 4.8, 4.2, 4.5,
         '«server» Cloud VM / Dev Machine',
         ['FastAPI  :8000  (uvicorn)',
          'XGBoost Service',
          'ANUGA Simulation Engine',
          'APScheduler (async)',
          'Email Service  (aiosmtplib)',
          '/maps  static file server'],
         nc=BLL, tc=BL)

    node(5.2, 7.2, 3.6, 1.8,
         '«browser» Client',
         ['React 18  +  TypeScript  (Vite)',
          'Leaflet.js  +  Recharts'],
         nc=TL, tc=T)

    node(5.2, 4.6, 3.6, 2.2,
         '«cloud» MongoDB Atlas',
         ['users  collection',
          'subscribers  collection',
          'site_config  collection'],
         nc=GNL, tc=GN)

    node(5.2, 1.5, 3.6, 2.7,
         '«local» SQLite',
         ['predictions  table',
          '(aiosqlite + SQLAlchemy)'],
         nc=ORL, tc=OR)

    node(9.6, 6.5, 4.8, 2.8,
         '«external» Open-Meteo APIs',
         ['ERA5 Rainfall  (archive + forecast)',
          'GloFAS v4  Discharge',
          'Copernicus DEM  Elevation',
          'Nominatim  Geocoding'],
         nc=PUL, tc=PU)

    node(9.6, 3.0, 4.8, 3.1,
         '«external» Gmail SMTP',
         ['TLS  port 587',
          'App Password auth',
          'HTML alert emails'],
         nc=RDL, tc=RD)

    # ── Communication paths ───────────────────────────────────────────────────
    def comm(x1, y1, x2, y2, proto, c=GR):
        ln(ax, x1, y1, x2, y2, c=c, lw=1.8, zorder=1)
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.2, proto,
                ha='center', va='bottom', fontsize=6.5, color=c,
                bbox=dict(boxstyle='round,pad=0.08', facecolor=BG,
                          edgecolor='none', alpha=0.9), zorder=4)

    # Browser ↔ FastAPI
    comm(5.2, 8.1, 4.5, 8.1, 'HTTP REST\n(Vite proxy → :8000)', c=BL)
    # FastAPI ↔ MongoDB
    comm(4.5, 5.8, 5.2, 5.8, 'MongoDB Wire Protocol\n(Motor async driver)', c=GN)
    # FastAPI ↔ SQLite
    comm(4.5, 3.5, 5.2, 3.5, 'SQLAlchemy\naiosqlite', c=OR)
    # FastAPI ↔ Open-Meteo
    comm(4.5, 7.2, 9.6, 8.0, 'HTTPS REST\n(aiohttp)', c=PU)
    # FastAPI ↔ Gmail
    comm(4.5, 5.0, 9.6, 4.6, 'SMTP\nTLS :587', c=RD)

    save(fig, '08_deployment_diagram.png')

# =============================================================================
# MAIN
# =============================================================================
def main():
    print('\nHydroAI Diagram Generator')
    print('─' * 36)
    d1_activity()
    d2_usecase()
    d3_class()
    d4_er()
    d5_seq_predict()
    d6_seq_scheduler()
    d7_state()
    d8_deployment()
    print('─' * 36)
    print(f'All diagrams saved to:\n  {DIR}')

if __name__ == '__main__':
    main()
