from flask import Flask, render_template, request
from dotenv import load_dotenv
import requests
import os
import joblib

# APP INIT

app = Flask(__name__)
load_dotenv()

# API CONFIG 

API_KEY = os.getenv("API_KEY")

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# MODEL LOAD 

MODEL_PATH = "models/weather_model.pkl"

try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully")
except Exception as e:
    model = None
    print("❌ Model loading failed:", e)
    # ---------------- HOME ---------------- #

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


#  WEATHER AND FORECAST

@app.route("/weather", methods=["POST"])
def weather():
    try:
        city = request.form.get("city")

        if not city:
            return render_template("index.html", error="Please enter a city name")
        

#  CURRENT WEATHER 
        city = city.strip()
        query = f"{city},IN"
        url = f"{WEATHER_URL}?q={query}&appid={API_KEY}&units=metric"
           
        response = requests.get(url)
        data = response.json()
     
        if response.status_code != 200 or "main" not in data:
            return render_template("index.html", error="City not found")

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        pressure = data["main"]["pressure"]
        feels_like = data["main"]["feels_like"]

        icon = data["weather"][0]["icon"]   
        description = data["weather"][0]["description"]
        country = data["sys"]["country"]

# ML PREDICTION 
        if model:
            prediction = model.predict([[temp, humidity, wind]])
            prediction_text = "🌧️ Rain Expected" if prediction[0] == 1 else "🌤️ No Rain Expected"
        else:
            prediction_text = "⚠️ Model not loaded"

        weather_data = {
            "city": city,
            "country": country,
            "temp": temp,
            "humidity": humidity,
            "wind": wind,
            "pressure": pressure,
            "feels_like": feels_like,
            "icon": icon,
            "description": description,
            "prediction": prediction_text
        }

# 5 DAY FORECAST

        forecast_response = requests.get(
        f"{FORECAST_URL}?q={query}&appid={API_KEY}&units=metric"
)
        forecast_data = forecast_response.json()

        forecast_list = []

        if "list" in forecast_data:
            for i in range(0, len(forecast_data["list"]), 8):
                day = forecast_data["list"][i]
                forecast_list.append({
                    "day": day["dt_txt"].split(" ")[0],
                    "temp": day["main"]["temp"],
                    "icon": day["weather"][0]["icon"]
                })

        return render_template(
            "index.html",
            weather=weather_data,
            forecast=forecast_list
        )

    except Exception as e:
        print("ERROR:", e)
        return render_template("index.html", error=str(e))


# RUN APP 

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)