from app.services.data_fetcher import fetch_data
from app.services.predictor import predict

data = fetch_data()
result = predict(data)

print("Data:", data)
print("Prediction:", result)