import requests
import pandas as pd
from io import StringIO

# Define the API endpoint for regional (global bounding box) and base parameters
base_url = "https://power.larc.nasa.gov/api/temporal/daily/regional"
base_params = {
    "parameters": "PRECTOTCORR",  # Limited to one parameter for regional endpoint
    "community": "AG",
    "longitude_min": -180,  # Global bounding box (may still cause issues due to size)
    "longitude_max": 180,
    "latitude_min": -90,
    "latitude_max": 90,
    "format": "CSV"
}

# Initialize an empty DataFrame to store all data
all_data = pd.DataFrame()

# Loop over years (2005–2024) for September 8–14
for year in range(2005, 2025):
    params = base_params.copy()
    params["start"] = f"{year}0908"  # September 8
    params["end"] = f"{year}0914"    # September 14

    # Make the API request
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {year}: {e}")
        continue

    # Load CSV from memory (no temp file)
    try:
        df = pd.read_csv(StringIO(response.text), skiprows=13)  # Adjusted to skip 13 metadata lines
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"Error processing data for {year}: {e}")
        continue

# Save combined data
all_data.to_csv("global_weather_2005_2024.csv", index=False)
print("Combined data saved to global_weather_2005_2024.csv")

# Calculate baseline rain probability (with check for empty data)
if not all_data.empty:
    rain_days = len(all_data[all_data["PRECTOTCORR"] > 0])
    total_days = len(all_data)
    rain_probability = (rain_days / total_days) * 100 if total_days > 0 else 0
    print(f"Baseline rain probability (Sep 8–14, 2005–2024, global average): {rain_probability:.2f}%")
else:
    print("No data loaded; verify API request parameters and limits.")