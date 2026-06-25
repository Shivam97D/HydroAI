# Front Matter — HydroAI Final Project Report

---

## Title Page

**A FINAL PROJECT REPORT ON**

# HYDROAI: HYBRID PHYSICS–AI FLOOD FORECASTING AND RISK ASSESSMENT SYSTEM

**SUBMITTED TO THE SAVITRIBAI PHULE PUNE UNIVERSITY, PUNE**

IN PARTIAL FULFILMENT OF THE REQUIREMENTS
FOR THE AWARD OF THE DEGREE

**BACHELOR OF ENGINEERING**
In
**COMPUTER ENGINEERING**
Of
**SAVITRIBAI PHULE PUNE UNIVERSITY**

By

| Student Name | Roll No. |
|---|---|
| SANIDHYA RISHIRAJ NAIK | 72231347M |
| JANHAVI ABHIJIT LONARI | 72231273D |
| ONKAR RAJENDRA GAIKWAD | 72230991M |
| SHIVAM GORAKSHA DAHIFALE | 72230889C |

**Under the guidance of**
Prof. S. P. Bholane

**DEPARTMENT OF COMPUTER ENGINEERING**
SINHGAD COLLEGE OF ENGINEERING, PUNE-41
Accredited by NAAC with A+

**2025–26**

> 📷 **[INSERT PHOTO: SCOE college building / department banner — front page]**

---

## Certificate

**Sinhgad Technical Education Society**
**Sinhgad College of Engineering, Pune-41**
**Department of Computer Engineering**

### CERTIFICATE

**Date:**

This is to certify that the Final Project Report entitled

**"HydroAI: Hybrid Physics–AI Flood Forecasting and Risk Assessment System"**

Submitted by

| Student Name | Roll No. |
|---|---|
| SANIDHYA RISHIRAJ NAIK | 72231347M |
| JANHAVI ABHIJIT LONARI | 72231273D |
| ONKAR RAJENDRA GAIKWAD | 72230991M |
| SHIVAM GORAKSHA DAHIFALE | 72230889C |

is a bonafide work carried out by them under the supervision of **Prof. S. P. Bholane** and it is approved for the partial fulfilment of the requirements of Savitribai Phule Pune University, Pune for the award of the degree of **Bachelor of Engineering (Computer Engineering)** during the year **2025–26**.

---

**Prof. S. P. Bholane** &emsp;&emsp;&emsp;&emsp;&emsp;&emsp; **Dr. R. H. Borhade**
Guide &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; Head
Department of Computer Engineering &emsp; Department of Computer Engineering

**Dr. S. D. Lokhande**
Principal
Sinhgad College of Engineering

---

## Acknowledgement

Projects are great opportunities offered to those who are specialising in certain skills and career development. This will help aspirants develop working ethics and build strong professional foundations. The journey from student to professional, with the aim of learning the practical aspects of engineering, has been a memorable experience filled with invaluable lessons.

We express our deep and sincere gratitude to our guide **Prof. S. P. Bholane**, whose continuous guidance, supervision, and timely feedback helped us navigate the challenges encountered during this project. His expertise in software engineering and his patience in discussing technical nuances have been the cornerstone of this work.

Special thanks to the **Head of Department, Dr. R. H. Borhade**, and **Principal, Dr. S. D. Lokhande**, for their expert suggestions and constant encouragement. We are sincerely grateful for the infrastructure and academic environment provided by Sinhgad College of Engineering, which made this project possible.

We thank the broader open-source community, including contributors to **ANUGA Hydro**, **Open-Meteo**, **FastAPI**, **React**, and **XGBoost** — whose freely available tools formed the technical backbone of HydroAI.

Last but not least, our sincere gratitude to our families, classmates, and all those who knowingly or unknowingly supported us in turning this project into a working system.

---

## Abstract

Floods are one of the most frequent and devastating natural disasters in India, causing massive loss of life, infrastructure damage, and economic disruption every monsoon season. Traditional flood forecasting methods often suffer from poor spatial resolution, computational delays, and a lack of real-time data integration.

This project, **"HydroAI: Hybrid Physics–AI Flood Forecasting and Risk Assessment System"**, presents a fully implemented, open-source flood intelligence platform that combines machine learning with hydrodynamic modelling. The system ingests live meteorological and hydrological data from open APIs — specifically **ERA5 reanalysis rainfall** from Open-Meteo and **GloFAS v4 river discharge** — to generate real-time flood risk predictions using a trained **XGBoost classifier**.

For high-risk events (risk score ≥ 0.6), the system triggers an **ANUGA hydraulic simulation** using a 2D shallow-water (Saint-Venant) solver over a Copernicus DEM elevation grid, producing pixel-accurate flood depth maps rendered as interactive **GeoJSON overlays** on a Leaflet.js map.

The platform additionally provides a **subscriber alert system** (Gmail SMTP, APScheduler-based cron), **JWT-authenticated user accounts**, an **admin site configuration panel**, a **flood awareness education page**, and a complete **prediction history** with hydrograph visualisation.

The system was evaluated on the **Pune Mutha–Mula river reach** (18.52°N, 73.86°E; ~2,030 km² catchment) and demonstrated high prediction accuracy (AUC > 0.93, NSE ≈ 0.88, RMSE ≤ 0.42 m) across historical flood events. The web application runs on a FastAPI backend with a React + TypeScript frontend, deployable via Docker on any standard cloud platform.

**Keywords:** Flood Forecasting, Hydrodynamic Modelling, ANUGA, XGBoost, ERA5, GloFAS, Real-Time Prediction, Disaster Management, Saint-Venant Equations, React, FastAPI

---

## Abbreviations

| Abbreviation | Full Form |
|---|---|
| DEM | Digital Elevation Model |
| ERA5 | ECMWF Reanalysis v5 (Rainfall/Climate Data) |
| GloFAS | Global Flood Awareness System (GEO/Copernicus) |
| ANUGA | Australian National University / Geoscience Australia Hydrodynamic Solver |
| XGBoost | Extreme Gradient Boosting |
| SRS | System Requirement Specification |
| API | Application Programming Interface |
| REST | Representational State Transfer |
| JWT | JSON Web Token |
| NSE | Nash–Sutcliffe Efficiency |
| RMSE | Root Mean Square Error |
| AUC | Area Under the ROC Curve |
| GIS | Geographic Information System |
| UML | Unified Modelling Language |
| SDLC | Software Development Life Cycle |
| GeoJSON | Geographic JavaScript Object Notation |
| SMTP | Simple Mail Transfer Protocol |
| KLOC | Kilo Lines of Code |
| COCOMO | Constructive Cost Model |
| NDMA | National Disaster Management Authority |
| IMD | India Meteorological Department |
| CWC | Central Water Commission |
| SRTM | Shuttle Radar Topography Mission |
| GUI | Graphical User Interface |
| ORM | Object-Relational Mapping |
| CORS | Cross-Origin Resource Sharing |
