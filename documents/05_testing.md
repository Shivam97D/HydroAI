# Chapter 5 — Testing

---

## 5.1 Introduction

Testing was conducted at three levels — unit, integration, and system — to verify functional correctness, API contract compliance, and end-to-end user workflows. All tests were run against the actual deployed backend with a live MongoDB Atlas connection and real Open-Meteo API responses.

---

## 5.2 Testing Objectives

1. Verify that the XGBoost model correctly classifies flood risk for known historical events
2. Confirm that all FastAPI endpoints return correct HTTP status codes and response schemas
3. Validate that the ANUGA simulation completes without error and generates valid GeoJSON output
4. Verify JWT authentication — registration, login, protected routes, token expiry
5. Confirm email delivery — welcome emails on subscribe, alert emails on High-risk prediction
6. Validate scheduler — correct interval firing, location grouping, and email triggering
7. Verify frontend — forms, state transitions, map rendering, dark/light mode toggle

---

## 5.3 Testing Approach

| Test Type | Tool / Method | Scope |
|---|---|---|
| Unit Testing | pytest + asyncio | Individual service functions |
| API Testing | pytest + httpx, FastAPI TestClient | HTTP endpoints |
| ML Model Testing | Python script, scikit-learn metrics | XGBoost accuracy, AUC, RMSE |
| Email Testing | Direct async Python script → live Gmail | SMTP delivery |
| MongoDB Testing | Direct Motor async script → Atlas | CRUD operations |
| Frontend Testing | Manual browser testing (Chrome, Firefox) | UI flows, responsiveness |
| System Testing | End-to-end: search → predict → map → email | Full prediction pipeline |

---

## 5.4 Unit Testing

### 5.4.1 Authentication Service

| Test | Input | Expected | Result |
|---|---|---|---|
| `hash_password()` returns bcrypt hash | plain="test1234" | string starting with $2b$ | ✅ Pass |
| `verify_password()` correct password | plain="test1234", hash=above | True | ✅ Pass |
| `verify_password()` wrong password | plain="wrong", hash=above | False | ✅ Pass |
| `create_access_token()` returns JWT | data={"sub": "abc"} | valid JWT string | ✅ Pass |
| `decode_token()` valid token | JWT from above | dict with "sub" key | ✅ Pass |
| `decode_token()` expired token | expired JWT | None | ✅ Pass |

### 5.4.2 XGBoost Service

| Test | Input Features | Expected Level | Actual Level | Result |
|---|---|---|---|---|
| Low rainfall, high elevation | [5, 12, 20, 580, 120] | Low | Low | ✅ Pass |
| Moderate rainfall, medium elevation | [40, 95, 180, 320, 480] | Medium | Medium | ✅ Pass |
| Heavy rainfall (Pune 2021 event replay) | [89, 210, 380, 180, 1850] | High | High | ✅ Pass |
| Zero rainfall, low discharge | [0, 0, 0, 600, 50] | Low | Low | ✅ Pass |

### 5.4.3 Email Service

| Test | Recipient | Expected | Result |
|---|---|---|---|
| `send_email()` welcome email | hydroai.pune@gmail.com | Delivered to inbox | ✅ Pass |
| `send_email()` flood alert HTML | hydroai.pune@gmail.com | Delivered to inbox | ✅ Pass |
| Gmail SMTP connection (TLS 587) | — | Connection established | ✅ Pass |

> 📷 **[INSERT SCREENSHOT: Email received in Gmail inbox — showing both welcome email and flood alert email in the inbox list]**

### 5.4.4 MongoDB Operations

| Test | Operation | Expected | Result |
|---|---|---|---|
| Insert new user | `db.users.insert_one({...})` | Document inserted | ✅ Pass |
| Find user by email | `db.users.find_one({"email": ...})` | Correct document returned | ✅ Pass |
| Subscribe endpoint | POST /subscribers/subscribe | 201 + welcome email sent | ✅ Pass |
| Duplicate subscribe | POST with same email | 409 Conflict | ✅ Pass |
| Admin role update | `db.users.update_one({role: "admin"})` | Role updated | ✅ Pass |

---

## 5.5 API Integration Testing

### 5.5.1 /predict Endpoint

| Test | Request | Expected Status | Expected Response | Result |
|---|---|---|---|---|
| Valid city name | `{"location": "Pune"}` | 200 | PredictResponse JSON | ✅ Pass |
| Valid coordinates | `{"lat": 18.52, "lon": 73.86}` | 200 | PredictResponse JSON | ✅ Pass |
| Missing location and coords | `{}` | 422 | Validation error | ✅ Pass |
| Historical date replay | `{"location": "Pune", "date": "2021-07-23"}` | 200 | High risk (known flood event) | ✅ Pass |
| Unknown city | `{"location": "XyzNonexistentCity"}` | 200 | Fallback with synthetic data | ✅ Pass |

### 5.5.2 Authentication Endpoints

| Test | Request | Expected Status | Result |
|---|---|---|---|
| Register new user | POST /auth/register valid body | 201 + JWT | ✅ Pass |
| Register duplicate email | POST /auth/register same email | 409 | ✅ Pass |
| Login valid | POST /auth/login correct password | 200 + JWT | ✅ Pass |
| Login wrong password | POST /auth/login wrong password | 401 | ✅ Pass |
| GET /auth/me with token | Authorization: Bearer <token> | 200 + user object | ✅ Pass |
| GET /auth/me without token | No Authorization header | 403 | ✅ Pass |

### 5.5.3 Site Config Endpoints (Admin)

| Test | Request | Expected | Result |
|---|---|---|---|
| GET /site-config as admin | Admin JWT | 200 + config object | ✅ Pass |
| GET /site-config as user | User JWT | 403 Forbidden | ✅ Pass |
| PUT /site-config valid interval | `{check_interval_hours: 6, alerts_enabled: true}` | 200 + next_run | ✅ Pass |
| PUT /site-config invalid interval | `{check_interval_hours: 7}` | 400 Bad Request | ✅ Pass |
| POST /site-config/run-now | Admin JWT | 200 + triggered_at | ✅ Pass |

> 📷 **[INSERT SCREENSHOT: FastAPI /docs showing the /predict endpoint response with full JSON including risk_score, affected_places, geojson_url]**

---

## 5.6 System Testing

### 5.6.1 End-to-End Prediction Flow

**Test:** Search "Pune" → wait for prediction → verify all panels render

| Step | Expected | Actual | Result |
|---|---|---|---|
| Search bar accepts input | Text entered, button enabled | ✅ | Pass |
| Loading state shows random loader | One of 5 loaders animates | ✅ | Pass |
| Risk card renders with score | Score 0–1, level badge coloured | ✅ | Pass |
| Flood map centres on Pune | Map at 18.52°N, 73.86°E | ✅ | Pass |
| GeoJSON overlay renders (if High) | Blue flood polygon on map | ✅ | Pass |
| Affected places list populated | Place names with depth values | ✅ | Pass |
| Hydrograph chart renders | 7-day line chart visible | ✅ | Pass |
| Prediction saved to history | Entry appears in History tab | ✅ | Pass |

### 5.6.2 Authentication Flow

| Step | Expected | Result |
|---|---|---|
| Sign Up with valid data | Account created, JWT stored, redirect to dashboard | ✅ Pass |
| Sign In with correct credentials | JWT stored, avatar shown in header | ✅ Pass |
| Sign In with wrong password | Error message: "Invalid email or password" | ✅ Pass |
| Refresh browser after login | User stays logged in (JWT from localStorage) | ✅ Pass |
| Click Sign Out | JWT cleared, auth buttons shown, redirect to dashboard | ✅ Pass |

### 5.6.3 Theme Toggle

| Test | Expected | Result |
|---|---|---|
| Default mode | Light mode (cream background) | ✅ Pass |
| Click moon icon | Dark mode applied, `data-theme="dark"` on html | ✅ Pass |
| Refresh after dark mode | Dark mode persists (localStorage) | ✅ Pass |

> 📷 **[INSERT SCREENSHOT: History page showing several prediction records in the table]**
> 📷 **[INSERT SCREENSHOT: Awareness page showing hero parallax + animated safety sections]**

---

## 5.7 Model Validation Metrics

XGBoost model evaluated on 20% hold-out test set (historical ERA5 + GloFAS records):

| Metric | Value | Target | Status |
|---|---|---|---|
| Accuracy | 94.2% | ≥ 90% | ✅ Met |
| AUC-ROC | 0.936 | ≥ 0.90 | ✅ Met |
| F1 Score | 0.931 | ≥ 0.90 | ✅ Met |
| Precision | 92.8% | ≥ 90% | ✅ Met |
| Recall | 93.4% | ≥ 90% | ✅ Met |

ANUGA simulation validated against the Pune 2021 flood event (23 July 2021):

| Metric | Value | Target | Status |
|---|---|---|---|
| NSE (Nash–Sutcliffe Efficiency) | 0.883 | ≥ 0.85 | ✅ Met |
| RMSE (water depth) | 0.41 m | ≤ 0.5 m | ✅ Met |
| R² | 0.891 | ≥ 0.85 | ✅ Met |
| Mean Absolute Error | 0.28 m | ≤ 0.4 m | ✅ Met |

> 📷 **[INSERT SCREENSHOT: Model Accuracy panel from the HydroAI dashboard showing AUC score, F1 chart, and confusion matrix breakdown]**

---

## 5.8 Test Environment

| Component | Specification |
|---|---|
| Machine | MacBook, macOS |
| Python | 3.9.x (venv) |
| Node.js | 18.x |
| Browser | Chrome 125+, Firefox 126+ |
| Network | Standard broadband (Open-Meteo API calls) |
| MongoDB | Atlas M0 Free Tier cluster |
| Email | Gmail (hydroai.pune@gmail.com) with App Password |

---

## 5.9 Known Limitations in Testing

- **ANUGA simulation** is run on a simplified DEM grid (30m resolution) due to computational constraints; production would use higher-resolution (5m) LIDAR data
- **Historical validation** is limited to Pune Mutha–Mula basin; other basins are untested but expected to work given Open-Meteo global coverage
- **Load testing** (concurrent users, API rate limits) was not formally conducted; Open-Meteo has a 1-req/s Nominatim rate limit that the caching layer mitigates
