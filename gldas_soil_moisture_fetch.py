import earthaccess
import pandas as pd
import xarray as xr
import os

# Authenticate with Earthdata (set credentials securely)
os.environ['EARTHDATA_USERNAME'] = 'your_username'  # Replace with your Earthdata username
os.environ['EARTHDATA_PASSWORD'] = 'your_password'  # Replace with your Earthdata password
auth = earthaccess.login(strategy="environment")

# Search for GLDAS-2.1 near-real-time data (e.g., last 7 days)
results = earthaccess.search_data(
    short_name="GLDAS_NOAH025_3H",
    version="2.1",
    cloud_hosted=True,
    temporal=("2025-09-19", "2025-09-25"),  # Adjust for recent period
    bounding_box=(139.65, 35.68, 139.65, 35.68)  # Tokyo point (lon min, lat min, lon max, lat max)
)

# Download the first result (netCDF file)
files = earthaccess.download(results[0], local_dir=".")

# Load and process soil moisture (0-10 cm)
ds = xr.open_dataset(files[0])
soil_moisture = ds['SoilMoi0_10cm_inst'].sel(lat=35.6762, lon=139.6503, method='nearest').mean().values  # Average over time

print(f"Average recent soil moisture (kg/m²): {soil_moisture:.2f}")

# Optional: Save to CSV for integration
df = pd.DataFrame({'soil_moisture': [soil_moisture]})
df.to_csv("tokyo_gldas_soil_moisture.csv", index=False)
print("GLDAS data saved to tokyo_gldas_soil_moisture.csv")