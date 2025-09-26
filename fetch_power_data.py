import requests
import pandas as pd

# Define the API endpoint and base parameters
base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
base_params = {
    "parameters": "PRECTOTCORR,RH2M,T2M_MAX,T2M_MIN,WS10M",
    "community": "AG",
    "longitude": 139.6503,  # Tokyo
    "latitude": 35.6762,
    "format": "CSV"
}

# Initialize an empty DataFrame to store all data
all_data = pd.DataFrame()

# Loop over years (2005–2024) for 20 years of data
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

    # Save to a temporary CSV
    temp_csv = f"tokyo_weather_{year}.csv"
    with open(temp_csv, "wb") as f:
        f.write(response.content)

    # Load and append to DataFrame
    try:
        df = pd.read_csv(temp_csv, skiprows=13)  # Adjusted to skip 13 metadata lines
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"Error processing CSV for {year}: {e}")
        continue

# Save combined data
all_data.to_csv("tokyo_weather_2005_2024.csv", index=False)
print("Combined data saved to tokyo_weather_2005_2024.csv")

# Calculate baseline rain probability
rain_days = len(all_data[all_data["PRECTOTCORR"] > 0])
total_days = len(all_data)
rain_probability = (rain_days / total_days) * 100 if total_days > 0 else 0
print(f"Baseline rain probability (Sep 8–14, 2005–2024): {rain_probability:.2f}%")