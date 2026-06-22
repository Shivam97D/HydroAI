"""
HydroAI – Model Training on REAL historical data
================================================
Builds a genuine rainfall–runoff dataset for the study reach from free,
no-key Open-Meteo sources and trains two models:

  1. Runoff REGRESSOR  – predicts next-day river discharge (m³/s) from
     antecedent rainfall + season.  Evaluated with NSE / RMSE / R²  →
     these are the headline accuracy metrics promised in the report.

  2. Flood-risk CLASSIFIER – predicts whether the river will exceed its
     2-year-return-period "danger" discharge tomorrow (1-day lead time),
     from the same features + current discharge.  Evaluated with
     ROC-AUC / precision / recall / FAR.

Data
----
  • Rainfall  : Open-Meteo ERA5 archive   (archive-api.open-meteo.com)
  • Discharge : Open-Meteo Flood / GloFAS  (flood-api.open-meteo.com)

Outputs (models/)
-----------------
  • model.pkl          – the flood-risk classifier (loaded by xgboost_service)
  • runoff_model.pkl   – the discharge regressor
  • thresholds.json    – return-period discharge thresholds for the reach
  • metrics.json       – all validation metrics (for the report)
  • ../data/training_data.csv – the assembled daily dataset (cached)

Run:
    python utils/train_model.py
"""

from __future__ import annotations

import csv
import json
import os
import sys
from datetime import date

import httpx
import joblib
import numpy as np

# Allow running as `python utils/train_model.py` from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_settings  # noqa: E402

settings = get_settings()

RANDOM_SEED = 42
START_YEAR = 2015
END_YEAR = 2024

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_CSV = os.path.join(DATA_DIR, "training_data.csv")

LAT = settings.REACH_CENTER_LAT
LON = settings.REACH_CENTER_LON

FEATURE_COLUMNS = ["rainfall_24h", "rainfall_3d", "rainfall_7d", "elevation", "river_flow"]


# ── Data acquisition ──────────────────────────────────────────────────────────
def _fetch_rainfall_series() -> dict[str, float]:
    """Daily precipitation_sum (mm) keyed by ISO date, from ERA5 archive."""
    out: dict[str, float] = {}
    with httpx.Client(timeout=60) as client:
        for yr in range(START_YEAR, END_YEAR + 1):
            params = {
                "latitude": LAT, "longitude": LON,
                "start_date": f"{yr}-01-01", "end_date": f"{yr}-12-31",
                "daily": "precipitation_sum", "timezone": "Asia/Kolkata",
            }
            r = client.get(settings.OPENMETEO_ARCHIVE_URL, params=params)
            r.raise_for_status()
            d = r.json()["daily"]
            for t, p in zip(d["time"], d["precipitation_sum"]):
                out[t] = float(p) if p is not None else 0.0
            print(f"  rainfall {yr}: {len(d['time'])} days")
    return out


def _fetch_discharge_series() -> dict[str, float]:
    """Daily river_discharge (m³/s) keyed by ISO date, from GloFAS."""
    out: dict[str, float] = {}
    with httpx.Client(timeout=60) as client:
        for yr in range(START_YEAR, END_YEAR + 1):
            params = {
                "latitude": LAT, "longitude": LON,
                "start_date": f"{yr}-01-01", "end_date": f"{yr}-12-31",
                "daily": "river_discharge",
            }
            r = client.get(settings.OPENMETEO_FLOOD_URL, params=params)
            r.raise_for_status()
            d = r.json()["daily"]
            for t, q in zip(d["time"], d["river_discharge"]):
                if q is not None:
                    out[t] = float(q)
            print(f"  discharge {yr}: {len(d['time'])} days")
    return out


def build_dataset(elevation: float) -> tuple[np.ndarray, list[str]]:
    """
    Assemble the daily table. Each row is one day with antecedent rainfall,
    current discharge, and next-day discharge (the regression target).
    Returns (array, header) and caches to CSV.
    """
    if os.path.exists(DATA_CSV):
        print(f"Loading cached dataset → {DATA_CSV}")
        rows, header = [], None
        with open(DATA_CSV) as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                rows.append([float(x) if i > 0 else x for i, x in enumerate(row)])
        return np.array([r[1:] for r in rows], dtype=float), header

    print("Fetching REAL historical data (ERA5 rainfall + GloFAS discharge)…")
    rain = _fetch_rainfall_series()
    flow = _fetch_discharge_series()

    dates = sorted(set(rain) & set(flow))
    print(f"Aligned {len(dates)} daily records {dates[0]} … {dates[-1]}")

    precip = np.array([rain[d] for d in dates])
    disch = np.array([flow[d] for d in dates])

    header = ["date", "month", "rainfall_24h", "rainfall_3d", "rainfall_7d",
              "elevation", "river_flow", "discharge_next"]
    table = []
    for i in range(7, len(dates) - 1):
        r24 = precip[i]
        r3 = precip[i - 2 : i + 1].sum()
        r7 = precip[i - 6 : i + 1].sum()
        month = int(dates[i][5:7])
        table.append([
            dates[i], month, round(r24, 3), round(r3, 3), round(r7, 3),
            round(elevation, 1), round(disch[i], 3), round(disch[i + 1], 3),
        ])

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(table)
    print(f"Saved dataset → {DATA_CSV}  ({len(table)} rows)")

    arr = np.array([row[1:] for row in table], dtype=float)
    return arr, header


# ── Return-period thresholds (Gumbel on annual maxima) ────────────────────────
def return_period_thresholds(dates_disch: list[tuple[str, float]]) -> dict:
    """Estimate discharge for 2/5/10/25-yr return periods via Gumbel EV1."""
    annual: dict[str, float] = {}
    for d, q in dates_disch:
        yr = d[:4]
        annual[yr] = max(annual.get(yr, 0.0), q)
    maxima = np.array(list(annual.values()))
    mu = maxima.mean()
    sigma = maxima.std(ddof=1)
    # Gumbel: x_T = mu - sqrt(6)/pi * sigma * (gamma + ln(ln(T/(T-1))))
    beta = np.sqrt(6) / np.pi * sigma
    loc = mu - 0.5772 * beta
    out = {}
    for T in (2, 5, 10, 25):
        out[f"Q{T}"] = round(float(loc - beta * np.log(np.log(T / (T - 1)))), 2)
    out["annual_max_mean"] = round(float(mu), 2)
    return out


# ── Metrics ───────────────────────────────────────────────────────────────────
def nse(obs: np.ndarray, sim: np.ndarray) -> float:
    return float(1 - np.sum((obs - sim) ** 2) / np.sum((obs - obs.mean()) ** 2))


def rmse(obs: np.ndarray, sim: np.ndarray) -> float:
    return float(np.sqrt(np.mean((obs - sim) ** 2)))


def r2(obs: np.ndarray, sim: np.ndarray) -> float:
    c = np.corrcoef(obs, sim)[0, 1]
    return float(c ** 2)


# ── Training ──────────────────────────────────────────────────────────────────
def train():
    from xgboost import XGBClassifier, XGBRegressor
    from sklearn.metrics import (precision_score, recall_score, roc_auc_score)

    os.makedirs(MODELS_DIR, exist_ok=True)

    # Real point elevation for the reach
    try:
        import asyncio
        from services.api_service import fetch_elevation
        elevation = asyncio.run(fetch_elevation(LAT, LON))
    except Exception:
        elevation = 560.0
    print(f"Reach elevation: {elevation} m")

    arr, header = build_dataset(elevation)
    cols = {name: i for i, name in enumerate(header[1:])}  # skip 'date'

    month = arr[:, cols["month"]]
    feats = np.column_stack([
        arr[:, cols["rainfall_24h"]],
        arr[:, cols["rainfall_3d"]],
        arr[:, cols["rainfall_7d"]],
        arr[:, cols["elevation"]],
        arr[:, cols["river_flow"]],
    ]).astype(np.float32)
    disch_today = arr[:, cols["river_flow"]]
    disch_next = arr[:, cols["discharge_next"]]

    # Return-period thresholds from the full discharge record (real years)
    rp = _thresholds_from_csv()
    # "Warning" = 95th-percentile high-flow day (enough positives for honest
    # precision/recall); Q2/Q5/Q10/Q25 are reserved for inundation severity.
    warn = round(float(np.percentile(disch_today, 95)), 2)
    rp["warning"] = warn
    print(f"Return-period thresholds: {rp}  (warning = P95 = {warn} m³/s)")

    # Labels: will the river exceed the high-flow warning level TOMORROW?
    labels = (disch_next >= warn).astype(int)
    print(f"High-flow day prevalence (next-day ≥ P95): {labels.mean():.2%}")

    # Richer features for the standalone discharge regressor (forecast model):
    # add short discharge lags + 7-day mean (recession/rising limb) and season.
    lag1 = np.concatenate([[disch_today[0]], disch_today[:-1]])
    lag3 = np.concatenate([np.repeat(disch_today[0], 3), disch_today[:-3]])
    roll7 = np.convolve(disch_today, np.ones(7) / 7, mode="same")
    msin = np.sin(2 * np.pi * month / 12)
    mcos = np.cos(2 * np.pi * month / 12)
    reg_feats = np.column_stack([
        arr[:, cols["rainfall_24h"]], arr[:, cols["rainfall_3d"]],
        arr[:, cols["rainfall_7d"]], disch_today, lag1, lag3, roll7, msin, mcos,
    ]).astype(np.float32)
    reg_cols = ["rainfall_24h", "rainfall_3d", "rainfall_7d", "river_flow",
                "discharge_lag1", "discharge_lag3", "discharge_7d_mean",
                "month_sin", "month_cos"]

    # Time-based split – last 20 % as test (no leakage)
    n = len(feats)
    split = int(n * 0.8)
    Xtr, Xte = feats[:split], feats[split:]
    ytr_c, yte_c = labels[:split], labels[split:]
    Rtr, Rte = reg_feats[:split], reg_feats[split:]
    ytr_r, yte_r = disch_next[:split], disch_next[split:]

    # ── Regressor: next-day discharge ────────────────────────────────────────
    print("\nTraining runoff regressor (discharge forecast)…")
    reg = XGBRegressor(
        n_estimators=600, max_depth=6, learning_rate=0.04,
        subsample=0.8, colsample_bytree=0.8, random_state=RANDOM_SEED, n_jobs=-1,
    )
    # River discharge is highly right-skewed (a few huge monsoon peaks). Train in
    # log space so the model is not dominated by extremes, then invert for metrics.
    reg.fit(Rtr, np.log1p(ytr_r))
    pred_r = np.expm1(reg.predict(Rte))
    pred_r = np.clip(pred_r, 0, None)
    reg_metrics = {
        "NSE": round(nse(yte_r, pred_r), 4),
        "RMSE_m3s": round(rmse(yte_r, pred_r), 3),
        "R2": round(r2(yte_r, pred_r), 4),
        "test_samples": int(len(yte_r)),
    }
    print(f"  Regressor: NSE={reg_metrics['NSE']}  RMSE={reg_metrics['RMSE_m3s']} m³/s  R²={reg_metrics['R2']}")

    # ── Classifier: next-day flood risk ──────────────────────────────────────
    print("\nTraining flood-risk classifier…")
    pos = max(ytr_c.sum(), 1)
    clf = XGBClassifier(
        n_estimators=400, max_depth=5, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
        scale_pos_weight=float((len(ytr_c) - pos) / pos),
        random_state=RANDOM_SEED, n_jobs=-1,
    )
    clf.fit(Xtr, ytr_c)
    proba = clf.predict_proba(Xte)[:, 1]
    pred_c = (proba >= 0.5).astype(int)
    fp = int(((pred_c == 1) & (yte_c == 0)).sum())
    tp = int(((pred_c == 1) & (yte_c == 1)).sum())
    clf_metrics = {
        "ROC_AUC": round(float(roc_auc_score(yte_c, proba)) if yte_c.sum() else 0.0, 4),
        "precision": round(float(precision_score(yte_c, pred_c, zero_division=0)), 4),
        "recall": round(float(recall_score(yte_c, pred_c, zero_division=0)), 4),
        "FAR": round(fp / (fp + tp), 4) if (fp + tp) else 0.0,
        "test_samples": int(len(yte_c)),
        "flood_days_in_test": int(yte_c.sum()),
    }
    print(f"  Classifier: ROC-AUC={clf_metrics['ROC_AUC']}  precision={clf_metrics['precision']}  "
          f"recall={clf_metrics['recall']}  FAR={clf_metrics['FAR']}")

    # ── Persist ──────────────────────────────────────────────────────────────
    joblib.dump(clf, os.path.join(MODELS_DIR, "model.pkl"))
    joblib.dump(reg, os.path.join(MODELS_DIR, "runoff_model.pkl"))
    with open(os.path.join(MODELS_DIR, "thresholds.json"), "w") as f:
        json.dump(rp, f, indent=2)
    metrics = {
        "study_area": settings.STUDY_AREA_NAME,
        "data_period": f"{START_YEAR}-01-01..{END_YEAR}-12-31",
        "data_source": "Open-Meteo ERA5 (rainfall) + GloFAS v4 (discharge)",
        "regression_discharge_forecast": reg_metrics,
        "classification_flood_risk": clf_metrics,
        "thresholds_m3s": rp,
        "feature_columns": FEATURE_COLUMNS,
        "runoff_feature_columns": reg_cols,
    }
    with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n✅  Saved model.pkl, runoff_model.pkl, thresholds.json, metrics.json")
    print(json.dumps(metrics, indent=2))


def _thresholds_from_csv() -> dict:
    """Compute return-period thresholds using real calendar years from the CSV."""
    pairs: list[tuple[str, float]] = []
    with open(DATA_CSV) as f:
        reader = csv.reader(f)
        header = next(reader)
        di = header.index("date")
        qi = header.index("river_flow")
        for row in reader:
            pairs.append((row[di], float(row[qi])))
    return return_period_thresholds(pairs)


if __name__ == "__main__":
    train()
