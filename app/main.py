from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

from app.services.data_fetcher import fetch_data
from app.services.predictor import predict
from app.services.alert_service import check_and_alert

app = FastAPI()

@app.get("/")
def home():
    return {"message": "HydroAI Backend Running 🚀"}


@app.get("/predict")
def get_prediction():
    data = fetch_data()
    result = predict(data)

    return {
        "data": data,
        "prediction": result
    }


# 🔁 Background job
def run_model():
    data = fetch_data()
    result = predict(data)

    print("AUTO:", result)

    # 🚨 Alert
    check_and_alert(result)


# ⏱️ Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(run_model, "interval", minutes=10)
scheduler.start()