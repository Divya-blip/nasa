from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import logging  # Add this import

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Helper function to fetch NASA POWER data
def fetch_nasa_data(lat, lon, start_year, end_year, parameters):
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": ",".join(parameters),
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()["properties"]["parameter"]
        return pd.DataFrame(data)
    else:
        raise ValueError("Failed to fetch NASA data")

# Endpoint for probability calculation
@app.route('/api/query', methods=['POST'])
def query_weather():
    data = request.json
    lat = data['lat']
    lon = data['lon']
    day_of_year = data['day_of_year']  # e.g., '07-04'
    conditions = data['conditions']    # e.g., {'very_hot': {'param': 'T2M_MAX', 'threshold': 32, 'operator': '>'}}
    start_year = 1981
    end_year = datetime.now().year - 1

    parameters = list(set(cond['param'] for cond in conditions.values()))
    df = fetch_nasa_data(lat, lon, start_year, end_year, parameters)

    # Filter to specific day of year across years
    df.index = pd.to_datetime(df.index, format='%Y%m%d')
    df_filtered = df[df.index.strftime('%m-%d') == day_of_year]

    results = {}
    for cond_name, cond in conditions.items():
        param_data = df_filtered[cond['param']]
        if cond['operator'] == '>':
            prob = (param_data > cond['threshold']).mean() * 100
        elif cond['operator'] == '<':
            prob = (param_data < cond['threshold']).mean() * 100
        # Add more operators as needed
        results[cond_name] = {
            'probability': round(prob, 2),
            'mean': param_data.mean(),
            'metadata': {'units': '°C' if 'T2M' in cond['param'] else 'mm/day' if 'PREC' in cond['param'] else 'm/s'}
        }

    # Prepare downloadable data (subset as CSV string)
    csv_data = df_filtered.to_csv()

    return jsonify({'results': results, 'csv_data': csv_data})

if __name__ == '__main__':
    app.run(debug=True)