import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.engine import URL
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# ==========================================
# 1. DATABASE CONNECTION & DATA PULL
# ==========================================
USER = "root"                  # <-- Your MySQL username
PASSWORD = "Your_MYSQL_Password"  # <-- Your working password
HOST = "127.0.0.1"
PORT = 3306
DB_NAME = "forgeiq"

db_url = URL.create(drivername="mysql+pymysql", username=USER, password=PASSWORD, host=HOST, port=PORT, database=DB_NAME)
engine = sqlalchemy.create_engine(db_url)

print("🔌 Pulling sensor telemetry and maintenance logs from MySQL...")

# Pull sensor readings
df_sensors = pd.read_sql("SELECT machine_id, timestamp, temperature_c, vibration_mmss, pressure_psi FROM machine_sensors", con=engine)
# Pull maintenance events (failures)
df_maint = pd.read_sql("SELECT machine_id, log_date, maintenance_type FROM maintenance_logs WHERE maintenance_type IN ('Unscheduled Breakdown', 'Corrective')", con=engine)

# Convert timestamps to date format for matching
df_sensors['date'] = pd.to_datetime(df_sensors['timestamp']).dt.date
df_maint['log_date'] = pd.to_datetime(df_maint['log_date']).dt.date

# ==========================================
# 2. FEATURE ENGINEERING (Labeling Failures)
# ==========================================
# We label a sensor reading as a "Failure" (1) if a breakdown happened on that machine on that day.
# Otherwise, it's labeled as "Normal" (0).
merged = pd.merge(
    df_sensors, 
    df_maint, 
    left_on=['machine_id', 'date'], 
    right_on=['machine_id', 'log_date'], 
    how='left'
)

# If maintenance type is not null, a failure occurred
merged['failed'] = np.where(merged['maintenance_type'].notna(), 1, 0)

# Select features and target
X = merged[['temperature_c', 'vibration_mmss', 'pressure_psi']]
y = merged['failed']

# ==========================================
# 3. TRAINING THE ML MODEL
# ==========================================
print("🧠 Training Random Forest Classifier to predict machine failures...")

# Split into training (80%) and testing (20%) sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Initialize and train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test data
y_pred = model.predict(X_test)

# ==========================================
# 4. RESULTS & ACCURACY
# ==========================================
print("\n🎯 Model Evaluation Results:")
print(f"Accuracy Score: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Normal Operating', 'Impending Failure']))

# Feature Importance (What is causing machines to break?)
importances = model.feature_importances_
features = X.columns
print("\n🔍 Sensor Impact on Machine Failures:")
for feature, importance in zip(features, importances):
    print(f" - {feature}: {importance * 100:.2f}% influence")