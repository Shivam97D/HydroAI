# predictor.py
#import joblib
#import numpy as np

#model = joblib.load("app/model/flood_model.pkl")

#def predict(data):
 #   features = np.array([[
  #      data["rainfall_24h"],
   #     data["rainfall_3d"],
    #   data["elevation"],
     #   data["river_level"]
    #]])
    
    #prediction = model.predict(features)[0]
    #prob = model.predict_proba(features)[0][1]

    #return {
     #   "flood_risk": int(prediction),
      #  "probability": float(prob)
    #}

import joblib
import numpy as np

# Load model once
model = joblib.load("app/model/flood_model.pkl")

def predict(data):
    features = np.array([[
        data["rainfall_24h"],
        data["rainfall_3d"],
        data["rainfall_7d"],
        data["elevation"],
        data["river_level"]
    ]])

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    # 🔥 Risk categorization
    if probability > 0.7:
        risk = "HIGH"
    elif probability > 0.4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    return {
        "prediction": int(prediction),
        "probability": float(probability),
        "risk_level": risk
    }