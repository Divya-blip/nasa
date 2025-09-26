import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load historical data
historical_df = pd.read_csv('tokyo_weather_2005_2024.csv')

# Create target variable: 1 if rain (PRECTOTCORR > 0), 0 otherwise
historical_df['rain'] = (historical_df['PRECTOTCORR'] > 0).astype(int)

# Features: RH2M, T2M_MAX, T2M_MIN, WS10M
features = ['RH2M', 'T2M_MAX', 'T2M_MIN', 'WS10M']
X = historical_df[features]
y = historical_df['rain']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate on test set
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f'Model accuracy on test set: {accuracy:.2f}')

# Load near-real-time data
recent_df = pd.read_csv('tokyo_near_real_time.csv', skiprows=13)

# Prepare recent features
recent_X = recent_df[features]

# Predict average rain probability for recent period
probabilities = model.predict_proba(recent_X)[:, 1]  # Probability of rain
avg_rain_prob = probabilities.mean() * 100
print(f'Predicted average rain probability for recent period: {avg_rain_prob:.2f}%')