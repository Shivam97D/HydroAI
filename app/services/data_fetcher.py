import requests
from datetime import datetime

# 🔑 API KEY
import os
API_KEY = os.getenv("OPENWEATHER_API_KEY")


# 📍 Kolhapur–Sangli Region
LAT = 16.78
LON = 74.40


# 🌧️ 1. Rainfall (OpenWeather)
#def get_rainfall_data():
 #   try:
  #      url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
   #     response = requests.get(url)
    #    data = response.json()

#        rainfall_24h = 0

        # Last 1 hour rainfall
 #       if "rain" in data and "1h" in data["rain"]:
  #          rainfall_24h = data["rain"]["1h"]

        # Temporary approximation (replace later with real historical API)
   #     rainfall_3d = rainfall_24h * 3
    #    rainfall_7d = rainfall_24h * 7

     #   return rainfall_24h, rainfall_3d, rainfall_7d

    #except Exception as e:
     #   print("Rainfall API Error:", e)
      #  return 0, 0, 0

import requests

def get_rainfall_data():
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={LAT}&longitude={LON}"
            f"&hourly=rain"
            f"&past_days=7"
            f"&timezone=auto"
        )

        response = requests.get(url)
        data = response.json()

        rain = data["hourly"]["rain"]  # hourly rainfall list

        # ✅ Last 24 hours
        rainfall_24h = sum(rain[-24:])

        # ✅ Last 3 days (72 hours)
        rainfall_3d = sum(rain[-72:])

        # ✅ Last 7 days (168 hours)
        rainfall_7d = sum(rain[-168:])

        return rainfall_24h, rainfall_3d, rainfall_7d

    except Exception as e:
        print("Rainfall API Error:", e)
        return 0, 0, 0

# ⛰️ 2. Elevation (Open-Meteo)
def get_elevation():
    try:
        url = f"https://api.open-meteo.com/v1/elevation?latitude={LAT}&longitude={LON}"
        response = requests.get(url)
        data = response.json()

        return data["elevation"][0]

    except Exception as e:
        print("Elevation API Error:", e)
        return 500  # fallback (avg elevation of region)


# 🌊 3. River Level (Krishna River - constant for now)
def get_river_level():
    # Approx normal river level in meters (adjust based on your dataset scale)
    return 6.5


# 🔗 4. Combined Data
def fetch_data():
    rainfall_24h, rainfall_3d, rainfall_7d = get_rainfall_data()
    elevation = get_elevation()
    river_level = get_river_level()

    return {
        "location": "Kolhapur-Sangli",
        "latitude": LAT,
        "longitude": LON,
        "rainfall_24h": rainfall_24h,
        "rainfall_3d": rainfall_3d,
        "rainfall_7d": rainfall_7d,
        "elevation": elevation,
        "river_level": river_level,
        "timestamp": datetime.now().isoformat()
    }