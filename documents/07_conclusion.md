# Chapter 7 — Conclusion

---

## 7.1 Summary of Work

HydroAI is a fully functional, open-source flood risk intelligence system developed as a final-year BE project at Savitribai Phule Pune University, SCOE Pune (Group 46, 2025–26). The project successfully delivers on all twelve functional requirements defined in the SRS and exceeds every quantitative performance target set at the planning stage.

The system integrates two complementary scientific approaches:

1. **Machine Learning (XGBoost):** A trained binary classifier that produces a flood risk score (0–1) and risk level (Low / Medium / High) in under 3 seconds using live Open-Meteo environmental data — no manual data collection required.

2. **Physics-Based Simulation (ANUGA):** A 2D shallow-water solver that generates spatial flood depth maps and identifies affected localities by name — triggered automatically only when the ML classifier detects a High-risk event.

These are served through a modern full-stack web application: a FastAPI async backend, a React 18 + TypeScript frontend, MongoDB Atlas for user management and subscriber storage, SQLite for prediction history, and an APScheduler-driven email alert system that delivers personalised HTML flood warnings to subscribers.

---

## 7.2 Objectives Achieved

| Objective | Status | Evidence |
|---|---|---|
| Real-time flood risk prediction for any Indian city | ✅ Complete | Nominatim geocoding + Open-Meteo APIs operational |
| XGBoost model trained on historical ERA5 + GloFAS data | ✅ Complete | AUC-ROC = 0.936, Accuracy = 94.2% |
| ANUGA 2D simulation with flood depth map output | ✅ Complete | GeoJSON overlay on Leaflet + PNG depth raster |
| Web dashboard with interactive Leaflet flood map | ✅ Complete | Dashboard with map, hydrograph, risk card all rendered |
| JWT-secured user authentication with role-based access | ✅ Complete | Admin/user roles, admin-only Site Config page |
| Email alert subscription and delivery | ✅ Complete | Welcome email + HTML flood alert verified via Gmail |
| Configurable APScheduler periodic flood checks | ✅ Complete | Interval [1h/3h/6h/12h/24h], persisted in MongoDB |
| NSE ≥ 0.85 for ANUGA simulation accuracy | ✅ Complete | NSE = 0.883 (Pune 2021 event) |
| RMSE ≤ 0.5 m for water depth estimates | ✅ Complete | RMSE = 0.41 m |
| Full deployment on GitHub (open-source) | ✅ Complete | https://github.com/Shivam97D/HydroAI |

---

## 7.3 Key Contributions

### 7.3.1 Hybrid ML + Physics Pipeline

The core contribution of HydroAI is the design of a two-stage prediction pipeline that uses ML for speed and physics for spatial accuracy. This approach avoids running an expensive 4-minute simulation for every low-risk query, while still producing detailed flood maps when the risk level warrants it.

### 7.3.2 Zero-Cost Data Infrastructure

By building entirely on Open-Meteo's free ERA5, GloFAS, and elevation APIs, and using Nominatim for geocoding, the system requires no paid data subscriptions. This makes it accessible to local disaster management bodies, NGOs, and research institutions in India without budget constraints.

### 7.3.3 End-to-End Alert System

The integration of APScheduler, MongoDB subscriber store, and aiosmtplib Gmail delivery creates a production-grade flood alert service. One prediction per unique subscriber location avoids redundant computation, and emails are sent only for High-risk events — minimising alert fatigue.

### 7.3.4 Open-Source and Reproducible

The entire codebase is published to GitHub with a comprehensive README, `.env.example` template, Docker deployment configuration, and this documentation. Any researcher or developer can reproduce the system from scratch.

---

## 7.4 Limitations

Despite meeting all stated objectives, the following constraints were identified:

1. **Single-basin training data:** The XGBoost model was trained primarily on the Pune (Mutha–Mula) basin. While the Open-Meteo API coverage is global, applying the model to basins with different hydrology (e.g., Himalayan snow-melt dominated rivers) may reduce accuracy without local retraining.

2. **DEM resolution:** Copernicus 30m DEM provides basin-scale accuracy. Street-level flood depth mapping would require 1–5m LIDAR data, which is not freely available for all Indian cities.

3. **Nominatim rate limit:** The Nominatim API enforces 1 request/second for free use. This is mitigated by the in-memory cache, but a production deployment with many concurrent users would need a paid geocoding API or a locally hosted Nominatim instance.

4. **No real-time IoT sensors:** The discharge input comes from GloFAS model output, not live gauge readings. CWC sensor integration would improve nowcasting accuracy, especially during rapidly evolving storm events.

5. **No mobile application:** The current system is web-only. A mobile app with push notifications would improve reach in rural areas where desktop access is limited.

---

## 7.5 Conclusion Statement

HydroAI demonstrates that a capable, scientifically rigorous flood warning system can be built entirely from open-source tools and free APIs at effectively zero cost. The project bridges the gap between research-grade hydrodynamic modelling and practical, accessible disaster management tools. It is not merely a prototype — it is a deployed, working system that sends real emails, runs live predictions, and stores historical data in a cloud database.

The team of four undergraduate students — Shivam Dahifale, Sanidhya Naik, Janhavi Lonari, and Onkar Gaikwad — has produced a system that is competitive in accuracy with commercially licensed alternatives (MIKE-FLOOD, HEC-RAS web tools) while being freely available to anyone who clones the repository.

> 📷 **[INSERT SCREENSHOT: Final dashboard view — the complete HydroAI interface showing a High-risk Pune prediction with all panels rendered]**
