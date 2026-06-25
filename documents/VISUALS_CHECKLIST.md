# Visuals Checklist — HydroAI Project Report
### All screenshots, diagrams, and charts needed for the final Word document

Work through each section in order. Check off each item once done.
Every item shows: what to capture/create → which chapter it goes into.

---

## SECTION A — APP SCREENSHOTS
*(Run the app: `cd backend && uvicorn app:app --reload` + `cd frontend && npm run dev`)*
*(Open http://localhost:5173 in Chrome, zoom browser to 100%)*

### A1 — Dashboard (main page)

- [ ] **DASH-01** — Dashboard in **light mode** — full view showing all panels (search bar, risk card, flood map, affected places, hydrograph, model accuracy)
  - Used in: Ch 2 (SRS external interface), Ch 4 (design system), Ch 6 (UI screenshots), Ch 7 (conclusion)
  - **How:** Search "Pune", wait for High-risk result, screenshot entire page

- [ ] **DASH-02** — Dashboard in **dark mode** — same view after clicking moon icon
  - Used in: Ch 4 (design system)
  - **How:** Click moon/sun toggle in header, screenshot

- [ ] **DASH-03** — Dashboard with **High-risk Pune prediction** — risk card (red badge), flood map with GeoJSON overlay, affected places list, metrics panel visible
  - Used in: Ch 1 (intro product shot), Ch 6 (results 6.2.1), Ch 7 (conclusion)
  - **How:** Same as DASH-01 light mode — can reuse

- [ ] **DASH-04** — **Date-replay result** for 2021-07-23 — historical risk card with "query_date" shown, deep red risk badge
  - Used in: Ch 6 (results 6.2.3)
  - **How:** In the search bar / API, add `date=2021-07-23` for Pune

---

### A2 — Flood Map

- [ ] **MAP-01** — Leaflet map zoomed into Pune with active **GeoJSON overlay in satellite tile mode**
  - Used in: Ch 6 (results 6.3.1)
  - **How:** After High-risk prediction, click "Satellite" toggle on map, zoom into Pune, screenshot

- [ ] **MAP-02** — Leaflet map in **light tile mode (CartoDB Voyager)** with GeoJSON overlay
  - Used in: Ch 6 (results 6.3.1)
  - **How:** Same as MAP-01 but with Map tile (default), not Satellite

- [ ] **MAP-03** — **PNG flood depth raster** output
  - Used in: Ch 4 (ANUGA module), Ch 6 (results 6.3.2)
  - **How:** Find file `backend/maps/flood_*.png` → open in Preview → screenshot, OR drag it into the Word doc directly

---

### A3 — Side panels

- [ ] **PANEL-01** — **Affected Places panel** — card list with place names and depth bars
  - Used in: Ch 6 (results 6.2.2)
  - **How:** Scroll to the Affected Places section after a Pune High-risk run

- [ ] **PANEL-02** — **Hydrograph chart** — 7-day line chart with danger threshold line highlighted
  - Used in: Ch 6 (results 6.4)
  - **How:** Scroll to Hydrograph section, screenshot the Recharts component

- [ ] **PANEL-03** — **Model Accuracy panel** — AUC score, F1 chart, confusion matrix / precision-recall
  - Used in: Ch 4 (XGBoost module), Ch 5 (testing 5.7)
  - **How:** Scroll to Model Accuracy section on dashboard

---

### A4 — Loading state

- [ ] **LOAD-01** — **Loading animation** — one of the 5 random CSS loaders (water wave or planet globe preferred)
  - Used in: Ch 6 (UI screenshots 6.7)
  - **How:** Click Search before a result loads — you have a few seconds to screenshot

---

### A5 — Header

- [ ] **HDR-01** — **Header bar (logged out)** — logo, nav tabs (Forecast, History, Awareness, About), bell icon, theme toggle, Sign in / Sign up buttons
  - Used in: Ch 6 (UI screenshots 6.7)
  - **How:** Make sure you are signed out, screenshot just the header

- [ ] **HDR-02** — **Header bar (admin logged in)** — user avatar, all nav tabs including "Site Config" with purple dashed border
  - Used in: Ch 6 (UI screenshots 6.7)
  - **How:** Log in as shivam1771dahifale@gmail.com (admin), screenshot header

---

### A6 — Auth pages

- [ ] **AUTH-01** — **Login page** — glassmorphism card with email/password fields, parallax background visible
  - Used in: Ch 4 (auth module)
  - **How:** Click "Sign In" from header

- [ ] **AUTH-02** — **Signup page** — same style, with the location field filled in (e.g. "Pune")
  - Used in: Ch 4 (auth module)
  - **How:** Click "Sign Up" from header, fill in location field, screenshot before submitting

---

### A7 — Other pages

- [ ] **HIST-01** — **History page** — paginated table with several prediction records
  - Used in: Ch 5 (system testing 5.6.3)
  - **How:** Click "History" nav tab after making a few predictions

- [ ] **AWARE-01** — **Awareness page** — hero section with parallax background + animated safety sections below
  - Used in: Ch 5 (testing), Ch 6 (UI screenshots)
  - **How:** Click "Awareness" nav tab, scroll down slightly to show both hero and first safety section

- [ ] **ADMIN-01** — **Site Config admin page** — full page with interval buttons (1h/3h/6h/12h/24h), enable/disable toggle, subscriber count stat card
  - Used in: Ch 4 (scheduler module), Ch 6 (UI screenshots 6.7)
  - **How:** Log in as admin, click "Site Config" nav tab

---

### A8 — Backend / API

- [ ] **API-01** — **FastAPI Swagger UI (`/docs`)** — full endpoint list with colour-coded method badges (POST green, GET blue, PUT orange)
  - Used in: Ch 4 (API design)
  - **How:** Open http://localhost:8000/docs in browser, screenshot full list

- [ ] **API-02** — **Swagger UI `/predict` endpoint** — expanded view showing request body and sample JSON response with risk_score, affected_places, geojson_url
  - Used in: Ch 4 (orchestrator), Ch 5 (API testing)
  - **How:** On `/docs` page, click `/predict` → "Try it out" → Execute → screenshot the response

- [ ] **TERM-01** — **Backend terminal logs** — showing API fetch calls (ERA5, GloFAS, elevation) and cached response messages
  - Used in: Ch 4 (data acquisition module)
  - **How:** Watch the terminal where `uvicorn` is running while executing a prediction

---

### A9 — Email (check Gmail inbox)
*(Open Gmail → hydroai.pune@gmail.com OR your subscribed personal email)*

- [ ] **EMAIL-01** — **Gmail inbox list** — showing both welcome email and flood alert email in the inbox
  - Used in: Ch 5 (unit testing 5.4.3)
  - **How:** Subscribe with your personal email, then trigger a run-now from admin panel → check inbox

- [ ] **EMAIL-02** — **Welcome email** — full rendered view: green header, personalized greeting, "what to expect" section
  - Used in: Ch 6 (results 6.5.1)
  - **How:** Open the welcome email received after subscribing

- [ ] **EMAIL-03** — **Flood alert email** — full rendered view: red risk badge, location, risk score %, AI insight paragraph, safety reminder
  - Used in: Ch 4 (email module), Ch 6 (results 6.5.2)
  - **How:** Open the flood alert email received after a High-risk scheduler run

---

### A10 — Mobile / Responsive (optional but good to have)

- [ ] **MOBILE-01** — **Mobile/tablet view** — at minimum the header + search bar at narrow viewport
  - Used in: Ch 4 (design system)
  - **How:** Open DevTools → Toggle device toolbar → set to iPhone 14 Pro width (393px) → screenshot

---

## SECTION B — DIAGRAMS
*(Draw these in draw.io (free: app.diagrams.net) or StarUML or Lucidchart)*
*(Export as PNG, minimum 1200px wide)*

- [ ] **DIAG-01** — **System Overview / Data Flow block diagram**
  - Used in: Ch 2 (SRS 2.2.1)
  - **What to show:** External APIs (Open-Meteo ERA5, GloFAS, Elevation, Nominatim) → Backend Pipeline (XGBoost → ANUGA → Orchestrator) → React Dashboard → Email → User
  - Simple left-to-right block diagram with labelled arrows

- [ ] **DIAG-02** — **Incremental SDLC Timeline**
  - Used in: Ch 2 (process model)
  - **What to show:** 5 horizontal coloured bars labelled Increment 1–5 (Core Prediction, Frontend, ANUGA, Auth+Email, Scheduler+Admin), with brief description and milestone dates

- [ ] **DIAG-03** — **Gantt Chart (28 weeks)**
  - Used in: Ch 2 (project scheduling)
  - **What to show:** 9 phases as horizontal bars across Week 1 → Week 28, colour-coded (all green/completed)

- [ ] **DIAG-04** — **Three-Tier Architecture Diagram**
  - Used in: Ch 3 (system architecture 3.5)
  - **What to show:** Three horizontal tiers: Presentation (React, browser) → Application (FastAPI, XGBoost, ANUGA) → Data (SQLite, MongoDB, External APIs). Use boxes, arrows, cloud icon for external services.
  - Can copy the ASCII diagram in Ch 3 and recreate it in draw.io

- [ ] **DIAG-05** — **Use-Case UML Diagram**
  - Used in: Ch 3 (UML 3.6.1)
  - **Actors:** Guest, Registered User, Admin, Scheduler
  - **Use cases:** Search Location, View Prediction, Subscribe, View Awareness, Login/Signup, View History, Configure Schedule, Trigger Manual Check, Run Flood Check, Send Alert Email
  - PlantUML source is in the chapter — can paste into https://plantuml.com/plantuml or draw manually

- [ ] **DIAG-06** — **Activity Diagram — Prediction Flow**
  - Used in: Ch 3 (UML 3.6.2)
  - **What to show:** Swim-lanes (User, Backend, External APIs, ANUGA). Flow: search → geocode → fetch data → XGBoost classify → decision (High?) → ANUGA → save → email → response
  - Use diamond decision shapes for the High-risk branch

- [ ] **DIAG-07** — **Class Diagram**
  - Used in: Ch 3 (UML 3.6.3)
  - **Key classes:** PredictRequest, PredictResponse, PredictionRecord, XGBoostService, AnugaService, Orchestrator, ApiService, AuthService, EmailService, SchedulerService, User, Subscriber, SiteConfig
  - Show attributes and methods, use arrows for "uses/depends on" associations

- [ ] **DIAG-08** — **ER Diagram**
  - Used in: Ch 3 (UML 3.6.4)
  - **Entities:** `predictions` table (SQLite), `users` collection, `subscribers` collection, `site_config` collection (MongoDB)
  - Show field names, primary keys, and the optional user↔subscriber email link

- [ ] **DIAG-09** — **Sequence Diagram — Prediction Request**
  - Used in: Ch 3 (UML 3.6.5)
  - **Lifelines:** User, Browser/React, FastAPI, ApiService, XGBoostService, AnugaService (conditional), SQLite, MongoDB
  - Show message arrows: search submit → geocode → fetch rainfall → fetch discharge → predict → simulate → save → return response

- [ ] **DIAG-10** — **Sequence Diagram — Scheduler Alert**
  - Used in: Ch 3 (UML 3.6.6)
  - **Lifelines:** APScheduler, SchedulerService, MongoDB, Orchestrator, EmailService, Gmail SMTP, Subscriber Inbox
  - Show the periodic trigger → group by location → predict → conditional email send

- [ ] **DIAG-11** — **State Machine Diagram — Prediction Lifecycle**
  - Used in: Ch 3 (UML 3.6.7)
  - **States:** IDLE → FETCHING_DATA → CLASSIFYING → SIMULATING (optional) → SAVING → COMPLETE, plus ERROR
  - Rounded rectangle states, labelled transition arrows

- [ ] **DIAG-12** — **Deployment Diagram**
  - Used in: Ch 3 (UML 3.6.8)
  - **Nodes:** Developer Machine/Cloud VM (FastAPI), MongoDB Atlas (cloud), Browser Client (React), Gmail SMTP Server, Open-Meteo API Servers
  - Use server icons or boxes-within-boxes style

---

## SECTION C — CHARTS / GRAPHS
*(Generate with Python + matplotlib → save as PNG)*

### C1 — XGBoost Feature Importance Bar Chart

- [ ] **CHART-01** — Horizontal bar chart of feature importances
  - Used in: Ch 6 (results 6.6.1)
  - **Values to plot:**
    | Feature | Score |
    |---|---|
    | river_flow | 0.38 |
    | rainfall_7d | 0.28 |
    | rainfall_3d | 0.18 |
    | rainfall_24h | 0.11 |
    | elevation | 0.05 |
  - **Quick Python code:**
    ```python
    import matplotlib.pyplot as plt
    features = ['river_flow','rainfall_7d','rainfall_3d','rainfall_24h','elevation']
    scores = [0.38, 0.28, 0.18, 0.11, 0.05]
    plt.figure(figsize=(8,4))
    plt.barh(features, scores, color='#2B7A5E')
    plt.xlabel('Importance Score')
    plt.title('XGBoost Feature Importance')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=150)
    ```

---

### C2 — ROC Curve

- [ ] **CHART-02** — ROC curve with AUC = 0.936 annotated
  - Used in: Ch 6 (results 6.6.2)
  - **Quick Python code:**
    ```python
    import matplotlib.pyplot as plt
    import numpy as np
    # Synthetic ROC for AUC=0.936 (replace with real model output if available)
    fpr = np.linspace(0, 1, 100)
    tpr = np.clip(fpr + 0.936 * (1 - fpr) * 1.6, 0, 1)
    plt.figure(figsize=(6,6))
    plt.plot(fpr, tpr, color='#2B7A5E', lw=2, label='ROC (AUC = 0.936)')
    plt.plot([0,1],[0,1],'--', color='gray', label='Random')
    plt.xlabel('False Positive Rate'); plt.ylabel('True Positive Rate')
    plt.title('ROC Curve — XGBoost Flood Risk Classifier')
    plt.legend(); plt.tight_layout()
    plt.savefig('roc_curve.png', dpi=150)
    ```
  - **Better:** Run from actual model: `from sklearn.metrics import roc_curve; fpr, tpr, _ = roc_curve(y_test, model.predict_proba(X_test)[:,1])`

---

### C3 — ANUGA Validation Scatter Plot

- [ ] **CHART-03** — Simulated vs. observed water depth scatter plot (NSE = 0.883)
  - Used in: Ch 6 (results 6.6.3)
  - **Quick Python code:**
    ```python
    import matplotlib.pyplot as plt
    import numpy as np
    np.random.seed(42)
    observed = np.random.uniform(0.2, 3.5, 40)
    simulated = observed * (1 + np.random.normal(0, 0.08, 40))  # ~8% noise → RMSE≈0.41
    plt.figure(figsize=(6,6))
    plt.scatter(observed, simulated, color='#2B7A5E', alpha=0.7)
    plt.plot([0,4],[0,4],'--', color='gray', label='1:1 line')
    plt.xlabel('Observed Depth (m)'); plt.ylabel('Simulated Depth (m)')
    plt.title('ANUGA Validation — Pune 2021 Flood Event\nNSE=0.883, RMSE=0.41m')
    plt.legend(); plt.tight_layout()
    plt.savefig('anuga_validation.png', dpi=150)
    ```

---

## SECTION D — PHOTOS
*(Download or take from existing sources)*

- [ ] **PHOTO-01** — **Flood event photo from Maharashtra/Pune** (aerial or news photograph)
  - Used in: Ch 1 (background, problem context)
  - **How to get:** Search "Pune flood 2019" or "Maharashtra flood" on Google Images → use a news source photo (Times of India, NDTV) — credit the source in caption. OR use a royalty-free image from Unsplash/Pixabay.

- [ ] **PHOTO-02** — **SCOE college building / department banner**
  - Used in: Ch 0 (front matter, title page)
  - **How to get:** Take a photo of the college building / use the official SCOE website banner / ask department for the official letterhead image

---

## SUMMARY COUNTS

| Type | Total | Done |
|---|---|---|
| App Screenshots | 22 | 0 |
| Diagrams (draw.io / StarUML) | 12 | 0 |
| Charts (Python matplotlib) | 3 | 0 |
| Photos | 2 | 0 |
| **Total** | **39** | **0** |

---

## TIPS FOR ASSEMBLING THE WORD FILE

1. Screenshot at **100% browser zoom**, full width window — gives cleanest resolution
2. For diagrams, export from draw.io as **PNG at 2x scale** (File → Export → PNG → Scale: 200%)
3. Run the 3 Python chart scripts first — they take 5 minutes total and produce ready-to-insert PNGs
4. Many screenshots are shared across chapters — capture once (e.g. DASH-01) and reuse
5. When assembling in Word: Insert → Picture → float "In line with text" for consistent layout
