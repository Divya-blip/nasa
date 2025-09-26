import earthaccess
import xarray as xr
import pandas as pd
import os

# Authenticate with Earthdata (set credentials securely)
os.environ['divya_1602'] = 'divya_1602'  # Replace with your Earthdata username
os.environ['$s$X*@L7kj5d8#M'] = '$s$X*@L7kj5d8#M'  # Replace with your Earthdata password
auth = earthaccess.login(strategy="environment")

# Search for MERRA-2 data (example: M2T1NXSLV for surface variables, September 8-14, 2024)
results = earthaccess.search_data(
    short_name="M2T1NXSLV",  # MERRA-2 hourly tavg1_2d_slv_Nx (adjust for other collections)
    version="5.12.4",
    cloud_hosted=True,
    temporal=("2024-09-08", "2024-09-14")
)

# Download files (bulk download to current directory)
files = earthaccess.download(results, local_path=".")
# Process downloaded netCDF files (example: average precipitation)
all_data = pd.DataFrame()

for file in files:
    try:
        ds = xr.open_dataset(file)
        # Select variables (e.g., PRECTOT for precipitation, RH2M for humidity; adjust as needed)
        precip_avg = ds['PRECTOT'].mean(dim=['lat', 'lon']).values.item() if 'PRECTOT' in ds else 0  # Global average
        humidity_avg = ds['RH2M'].mean(dim=['lat', 'lon']).values.item() if 'RH2M' in ds else 0
        # Append to DataFrame (example with date from filename or metadata)
        date = file.split('.')[-2]  # Extract date from filename
        df = pd.DataFrame({'date': [date], 'avg_precip': [precip_avg], 'avg_humidity': [humidity_avg]})
        all_data = pd.concat([all_data, df], ignore_index=True)
    except Exception as e:
        print(f"Error processing {file}: {e}")

# Save combined data
all_data.to_csv("merra2_global_averages.csv", index=False)
print("Combined MERRA-2 data saved to merra2_global_averages.csv")

# Calculate baseline rain probability (example: assuming PRECTOT > 0 indicates rain)
rain_days = len(all_data[all_data["avg_precip"] > 0])
total_days = len(all_data)
rain_probability = (rain_days / total_days) * 100 if total_days > 0 else 0
print(f"Baseline rain probability: {rain_probability:.2f}%")