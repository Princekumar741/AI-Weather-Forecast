import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib

# Load Dataset
data = pd.read_csv("data/weather.csv")

# Features
X = data[["temperature", "humidity", "pressure"]]

# Target
y = data["next_day_temp"]

# Train Model
model = LinearRegression()
model.fit(X, y)

# Save Model
joblib.dump(model, "models/weather_model.pkl")

print("✅ AI Model Trained Successfully!")