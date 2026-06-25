# Chapter 1 — Introduction

---

## 1.1 Background and Basics

Floods are among the most recurrent hydrological disasters globally, occurring when water overflows onto normally dry land due to heavy rainfall, river overflow, storm surges, or drainage failure. India, with its diverse river basins and pronounced monsoon climate, experiences flooding almost every year, affecting millions of people and causing annual economic losses in the thousands of crores.

Flood prediction plays a critical role in minimising impact by enabling disaster management authorities to issue timely warnings and mobilise resources. Two principal approaches exist:

**Physics-based (hydrodynamic) models** solve the Saint-Venant shallow-water equations — representing mass and momentum conservation — to simulate water flow velocity, depth, and inundation extent over a digital elevation model (DEM). Tools such as ANUGA, HEC-RAS, and MIKE-FLOOD fall into this category. They are highly accurate but computationally expensive.

**Data-driven (machine learning) models** learn statistical patterns from historical rainfall and discharge records to predict flood risk scores rapidly. Models such as XGBoost, LSTM, and Random Forest excel in speed but lack physical interpretability.

**HydroAI** combines both approaches in a hybrid pipeline: an XGBoost classifier provides a near-instantaneous risk score from live data, and for high-risk events the system escalates to a full ANUGA hydrodynamic simulation that produces physically grounded flood depth maps. This design achieves both the speed needed for real-time alerting and the spatial accuracy required for emergency planning.

> 📷 **[INSERT PHOTO: Flood event photo from Maharashtra/Pune — aerial or news photograph — to illustrate the problem context]**

---

## 1.2 Literature Survey

| Sr. | Paper Title | Key Findings | Relevance |
|---|---|---|---|
| 1 | Flood Forecasting Using 2D Hydrodynamic Models: Godavari Basin (2022) | 2D hydrodynamic models provide accurate inundation mapping for Indian rivers | Validates physics-based simulation approach used in this project |
| 2 | Integration of Remote Sensing and GIS for Flood Risk Assessment (2021) | Sentinel-1 SAR data used to validate flood extent maps | Supports GeoJSON/Leaflet overlay approach in HydroAI |
| 3 | Data Assimilation for Flood Forecasting using ANUGA (2023) | ANUGA efficiently solves shallow-water equations for open-source flood prediction | Direct basis for the ANUGA simulation engine in our system |
| 4 | Machine Learning Aided Flood Forecasting (2022) | XGBoost and LSTM improve forecast lead time and precision | Validates choice of XGBoost as the risk classifier |
| 5 | GloFAS Global Flood Forecasting (Copernicus, 2020) | GloFAS v4 provides reliable global river discharge forecasts at daily resolution | Basis for using GloFAS API as primary discharge data source |
| 6 | ERA5 Reanalysis for Hydrological Modelling (ECMWF, 2021) | ERA5 provides high-quality historical and near-real-time rainfall data globally | Confirms suitability of Open-Meteo ERA5 archive for model input |
| 7 | Hybrid Physics–ML Models for Flood Prediction (2023) | Coupling hydrodynamic and ML models improves accuracy while reducing compute time | Direct motivation for the hybrid architecture of HydroAI |

Research consistently shows that coupling hydrodynamic modelling with real-time data and ML techniques significantly enhances prediction accuracy, reduces false alarm rates, and provides actionable flood risk intelligence for disaster management authorities.

---

## 1.3 Project Undertaken

HydroAI is a fully implemented, open-source flood intelligence platform built as a production-ready web application. The system is deployed for the **Pune Mutha–Mula river reach** (18.52°N, 73.86°E, approximately 2,030 km² catchment) but the pipeline is location-agnostic and covers any city with Open-Meteo API coverage.

The platform provides:
- Live flood risk scoring via XGBoost using real-time ERA5 rainfall and GloFAS discharge
- ANUGA hydraulic simulation for high-risk events, generating pixel-accurate flood depth maps
- Interactive web dashboard with Leaflet.js map, GeoJSON flood overlays, and affected place identification
- Subscriber alert system with scheduled cron-based checks and Gmail SMTP email notifications
- JWT-authenticated user accounts with role-based access (admin / user)
- Flood awareness education page and prediction history

### 1.3.1 Problem Definition

To design and implement a hybrid physics–AI flood prediction system that:

- Fetches live rainfall (ERA5) and river discharge (GloFAS) data automatically without manual input
- Classifies flood risk in real-time using a trained XGBoost model
- Triggers ANUGA hydrodynamic simulation for high-risk events to map inundation extents
- Renders interactive flood maps with affected localities in a web browser
- Sends proactive email alerts to registered subscribers based on scheduled risk assessments
- Provides an admin interface to configure alert frequency and monitor system status

### 1.3.2 Scope Statement

The system:

- Accepts a location name or coordinates; all environmental data is fetched automatically
- Produces risk scores (Low / Medium / High) with a confidence metric
- Runs 2D shallow-water simulation (ANUGA) for High-risk predictions
- Displays flood depth maps, affected place names, and 7-day hydrographs
- Manages user registration, login, and email alert subscriptions via a full-stack web interface
- Is scalable to any river basin covered by Open-Meteo APIs
- Is deployable on any cloud platform via Docker

**Out of scope:** IoT sensor integration, SMS alerting, multi-language support, and real-time satellite imagery (proposed as future work).

---

## 1.4 Objectives

1. To build a hybrid flood prediction system combining XGBoost ML with ANUGA hydrodynamic simulation
2. To integrate live ERA5 rainfall and GloFAS v4 river discharge data via open APIs (no API key required)
3. To produce interactive flood extent maps (GeoJSON + PNG overlays) rendered in a Leaflet.js dashboard
4. To achieve prediction accuracy: AUC ≥ 0.90, NSE ≥ 0.85, RMSE ≤ 0.5 m
5. To implement a complete subscriber alert system with scheduled flood checks and HTML email notifications
6. To build a secure, full-stack web application with JWT authentication and role-based access control
7. To document the system comprehensively for replication and future development

---

## 1.5 Motivation

Maharashtra experiences severe annual flooding — the 2021 Mahad collapse, 2022 Chiplun floods, and repeated inundation of Pune's Mutha riverbanks highlight the urgent need for localised, real-time flood forecasting tools.

Most existing systems rely on:
- Expensive proprietary software (MIKE-FLOOD, HEC-RAS licensed versions) inaccessible to small municipalities
- Centralised IMD/CWC forecasts with coarse spatial resolution (district-level, not ward-level)
- Manual data collection and delayed reporting

HydroAI addresses all three gaps: it is entirely open-source, provides street-level (Leaflet-rendered) flood maps, and operates automatically via scheduled API calls — enabling any state or local disaster management body to deploy it at negligible cost.

> 📷 **[INSERT PHOTO: Screenshot of the HydroAI dashboard showing a live prediction with the flood map and risk card — captures the final product]**

---

## 1.6 Organisation of Project Report

| Chapter | Title | Content |
|---|---|---|
| 1 | Introduction | Background, literature survey, problem definition, objectives |
| 2 | Project Planning & Management | SRS, process model, cost estimation, scheduling |
| 3 | Analysis & Design | IDEA matrix, architecture, UML diagrams (6 diagram types) |
| 4 | Implementation & Coding | System modules, code structure, API design, database schema |
| 5 | Testing | Unit, integration, and system test results with actual metrics |
| 6 | Results & Discussion | Screenshots, performance analysis, comparison with baselines |
| 7 | Conclusion | Summary of achievements and contributions |
| 8 | Future Work | Proposed enhancements and research directions |
| — | References | Academic papers and technical documentation |
