import pandas as pd
import numpy as np
from faker import Faker
import sqlalchemy
from datetime import datetime, timedelta
import random

# Initialize Faker for realistic names
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

from sqlalchemy.engine import URL

# ==========================================
# 1. DATABASE CONNECTION SETUP (SECURE BUILDER)
# ==========================================
USER = "root"          # <-- Your MySQL username
PASSWORD = "Your_MYSQL_Password"  # <-- Your password (even if it has special characters!)
HOST = "127.0.0.1"     # <-- Direct local IP
PORT = 3306
DB_NAME = "forgeiq"

# Build the connection object safely (escapes special characters)
connection_url = URL.create(
    drivername="mysql+pymysql",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

# Connect to MySQL and ensure database exists
engine_server = sqlalchemy.create_engine(connection_url)
with engine_server.connect() as conn:
    conn.execute(sqlalchemy.text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))

# Connect directly to our new database
db_url = URL.create(
    drivername="mysql+pymysql",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DB_NAME
)
engine = sqlalchemy.create_engine(db_url)

print("🚀 Connected to MySQL successfully. Starting data generation...")
# ==========================================
# 2. GENERATING FOUNDATIONAL TABLES
# ==========================================

# A. Factories (3 locations)
factories_data = [
    {"factory_id": 1, "location": "Austin, USA", "operating_cost_per_hr": 250.00},
    {"factory_id": 2, "location": "Munich, Germany", "operating_cost_per_hr": 290.00},
    {"factory_id": 3, "location": "Tokyo, Japan", "operating_cost_per_hr": 310.00}
]
df_factories = pd.DataFrame(factories_data)

# B. Production Lines (3 per factory = 9 total)
production_lines_data = []
line_id = 1
for f in factories_data:
    for line_type in ["Assembly", "Machining", "Packaging"]:
        production_lines_data.append({
            "line_id": line_id,
            "factory_id": f["factory_id"],
            "line_name": f"{f['location'].split(',')[0]} {line_type} Line",
            "max_capacity_per_hr": random.randint(100, 250)
        })
        line_id += 1
df_production_lines = pd.DataFrame(production_lines_data)

# C. Machines (3 to 4 per production line = 30 total)
machines_data = []
machine_types = ["Robotic Arm", "CNC Milling Machine", "Industrial Drill", "Laser Cutter", "Conveyor System"]
machine_id = 1
for line in production_lines_data:
    num_machines = random.randint(3, 4)
    for _ in range(num_machines):
        m_type = random.choice(machine_types)
        machines_data.append({
            "machine_id": machine_id,
            "line_id": line["line_id"],
            "machine_name": f"{m_type} #{machine_id}",
            "machine_type": m_type,
            "install_date": fake.date_between(start_date="-5y", end_date="-1y"),
            "status": "Operational"
        })
        machine_id += 1
df_machines = pd.DataFrame(machines_data)

# D. Products (10 unique aerospace/smart items manufactured)
products_data = []
product_names = [
    "Aero Turbine Blade", "Control Sensor Block", "Titanium Fastener Pack", 
    "Hydraulic Valve Actuator", "Carbon Composite Panel", "Electronic ECU Unit", 
    "Fuel Injector Nozzle", "Thermal Shield Plate", "Avionics Wiring Harness", "Fuselage Bracket"
]
for i, name in enumerate(product_names, 1):
    products_data.append({
        "product_id": i,
        "product_name": name,
        "sku": f"AP-{random.randint(100,999)}-{name[:3].upper()}",
        "target_cycle_time_sec": random.randint(15, 90),
        "unit_price": round(random.uniform(50.0, 1200.0), 2)
    })
df_products = pd.DataFrame(products_data)

# ==========================================
# 3. PUSHING FOUNDATIONAL TABLES TO MYSQL
# ==========================================
df_factories.to_sql("factories", con=engine, if_exists="replace", index=False)
df_production_lines.to_sql("production_lines", con=engine, if_exists="replace", index=False)
df_machines.to_sql("machines", con=engine, if_exists="replace", index=False)
df_products.to_sql("products", con=engine, if_exists="replace", index=False)

print(f"✅ Phase 1 Complete: Loaded Factories ({len(df_factories)}), Lines ({len(df_production_lines)}), Machines ({len(df_machines)}), Products ({len(df_products)}) into MySQL.")