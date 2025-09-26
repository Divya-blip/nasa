import requests
import pandas as pd

# Define the API endpoint and parameters for near-real-time data
base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": "PRECTOTCORR,RH2M,T2M_MAX,T2M_MIN,WS10M",
    "community": "AG",
    "longitude": 139.6503,  # Tokyo longitude
    "latitude": 35.6762,    # Tokyo latitude
    "start": "20250919",    # Adjust to recent dates (accounting for 1–3 day latency)
    "end": "20250922",
    "format": "CSV"
}

# Make the API request
try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error fetching near-real-time data: {e}")
    exit()

# Save the response to a CSV file
with open("tokyo_near_real_time.csv", "wb") as f:
    f.write(response.content)
print("Near-real-time data saved to tokyo_near_real_time.csv")

# Load and analyze the CSV
try:
    df = pd.read_csv("tokyo_near_real_time.csv", skiprows=13)  # Adjust skiprows based on metadata
    avg_precip = df["PRECTOTCORR"].mean()
    avg_humidity = df["RH2M"].mean()
    avg_temp_max = df["T2M_MAX"].mean()
    avg_temp_min = df["T2M_MIN"].mean()
    avg_wind_speed = df["WS10M"].mean()
    print(f"Average recent precipitation (mm/day): {avg_precip:.2f}")
    print(f"Average recent humidity (%): {avg_humidity:.2f}")
    print(f"Average recent max temperature (°C): {avg_temp_max:.2f}")
    print(f"Average recent min temperature (°C): {avg_temp_min:.2f}")
    print(f"Average recent wind speed (m/s): {avg_wind_speed:.2f}")
except Exception as e:
    print(f"Error processing CSV: {e}")