import pandas as pd
import numpy as np
from faker import Faker
import sqlalchemy
from sqlalchemy.engine import URL
from datetime import datetime, timedelta
import random

# Configuration
USER = "root"          # <-- Your MySQL username
PASSWORD = "Your_MYSQL_Password"  # <-- Your password
HOST = "127.0.0.1"
PORT = 3306
DB_NAME = "forgeiq"

# Reconnect to the database
db_url = URL.create(drivername="mysql+pymysql", username=USER, password=PASSWORD, host=HOST, port=PORT, database=DB_NAME)
engine = sqlalchemy.create_engine(db_url)

# Read back IDs from Phase 1 to ensure relational integrity
machines = pd.read_sql("SELECT machine_id, line_id FROM machines", con=engine)
products = pd.read_sql("SELECT product_id, unit_price FROM products", con=engine)

print("📅 Simulating 2 years of factory telemetry and production history...")

# Time windows: Past 730 days
end_date = datetime.now()
start_date = end_date - timedelta(days=730)

production_jobs = []
sensor_readings = []
maintenance_logs = []

job_id = 1
sensor_id = 1
maint_id = 1

current_time = start_date
while current_time < end_date:
    # Simulate a daily batch across active machines
    for _, machine in machines.iterrows():
        # 1. GENERATE PRODUCTION JOBS (Approx 10,000+ records over 2 years)
        if random.random() > 0.15:  # 85% chance a machine runs a job on any given day
            product = products.sample(n=1).iloc[0]
            quantity_produced = random.randint(50, 500)
            
            # Formulate realistic defect rates (usually 1-5%)
            defect_rate = random.uniform(0.01, 0.05)
            # Add an artificial "bad day" where defect rates spike to 25% for analytics flavor
            if random.random() > 0.96:
                defect_rate = random.uniform(0.15, 0.30)
                
            defects = int(quantity_produced * defect_rate)
            
            production_jobs.append({
                "job_id": job_id,
                "machine_id": machine["machine_id"],
                "product_id": int(product["product_id"]),
                "scheduled_date": current_time.date(),
                "quantity_produced": quantity_produced,
                "quantity_defective": defects,
                "runtime_hours": round(quantity_produced * random.uniform(0.02, 0.05), 2)
            })
            
            # 2. GENERATE IOT SENSOR READINGS (High-frequency data, approx 15,000+ records)
            # We sample data snapshots over time to watch for machine anomalies
            base_temp = random.choice([65, 70, 75])  # Baseline Celsius
            base_vib = random.uniform(1.2, 2.5)     # Baseline mm/s
            
            # Inject a failure sequence anomaly
            is_failing = random.random() > 0.97
            if is_failing:
                base_temp += random.uniform(25, 40)  # Overheating!
                base_vib += random.uniform(4.0, 7.5)   # Heavy shaking!

            sensor_readings.append({
                "sensor_reading_id": sensor_id,
                "machine_id": machine["machine_id"],
                "timestamp": current_time + timedelta(hours=random.randint(1, 23)),
                "temperature_c": round(base_temp + random.uniform(-2, 2), 2),
                "vibration_mmss": round(base_vib + random.uniform(-0.2, 0.2), 2),
                "pressure_psi": round(random.uniform(90, 120), 2)
            })
            
            # 3. GENERATE MAINTENANCE LOGS (Linked directly to our sensor anomalies)
            if is_failing:
                maintenance_logs.append({
                    "maintenance_id": maint_id,
                    "machine_id": machine["machine_id"],
                    "log_date": current_time.date(),
                    "maintenance_type": random.choice(["Unscheduled Breakdown", "Corrective"]),
                    "downtime_hours": round(random.uniform(2.0, 14.0), 1),
                    "repair_cost": round(random.uniform(300, 4500), 2),
                    "root_cause": random.choice(["Bearing Failure", "Motor Overheat", "Sensor Miscalibration", "Belt Misalignment"])
                })
                maint_id += 1
            elif random.random() > 0.98: # Routine regular tune-ups
                maintenance_logs.append({
                    "maintenance_id": maint_id,
                    "machine_id": machine["machine_id"],
                    "log_date": current_time.date(),
                    "maintenance_type": "Routine Preventative",
                    "downtime_hours": round(random.uniform(1.0, 4.0), 1),
                    "repair_cost": round(random.uniform(100, 500), 2),
                    "root_cause": "Scheduled Lubrication & Inspection"
                })
                maint_id += 1
                
            job_id += 1
            sensor_id += 1

    # Move forward 1 day
    current_time += timedelta(days=1)

# Convert arrays to dataframes
df_jobs = pd.DataFrame(production_jobs)
df_sensors = pd.DataFrame(sensor_readings)
df_maint = pd.DataFrame(maintenance_logs)

print("⚡ Injecting operational records into MySQL...")

# Push to MySQL
df_jobs.to_sql("production_jobs", con=engine, if_exists="replace", index=False)
df_sensors.to_sql("machine_sensors", con=engine, if_exists="replace", index=False)
df_maint.to_sql("maintenance_logs", con=engine, if_exists="replace", index=False)

total_records = len(df_jobs) + len(df_sensors) + len(df_maint)
print(f"✅ Phase 2 Complete!")
print(f"   - Production Jobs Created: {len(df_jobs)}")
print(f"   - Sensor IoT Readings Created: {len(df_sensors)}")
print(f"   - Maintenance Logs Created: {len(df_maint)}")
print(f"📊 Total Operational Database Size: {total_records} records loaded successfully.")