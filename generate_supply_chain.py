import pandas as pd
import numpy as np
from faker import Faker
import sqlalchemy
from sqlalchemy.engine import URL
from datetime import datetime, timedelta
import random

# Configuration
USER = "root"          # <-- Your MySQL username
PASSWORD = "Your_MYSQL_Password"  # <-- Your working password
HOST = "127.0.0.1"
PORT = 3306
DB_NAME = "forgeiq"

# Reconnect to the database
db_url = URL.create(drivername="mysql+pymysql", username=USER, password=PASSWORD, host=HOST, port=PORT, database=DB_NAME)
engine = sqlalchemy.create_engine(db_url)

# Read back reference data from database
factories = pd.read_sql("SELECT factory_id FROM factories", con=engine)
products = pd.read_sql("SELECT product_id FROM products", con=engine)
jobs = pd.read_sql("SELECT job_id, quantity_defective FROM production_jobs", con=engine)

print("🚚 Simulating global supply chain, inventory flow, and quality assurance logs...")

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ==========================================
# 1. SUPPLIERS (6 Global Vendors)
# ==========================================
suppliers_data = [
    {"supplier_id": 1, "supplier_name": "Titanium Metallurgy Corp", "country": "USA", "reliability_score": 94.5},
    {"supplier_id": 2, "supplier_name": "EuroAlloys GmbH", "country": "Germany", "reliability_score": 91.2},
    {"supplier_id": 3, "supplier_name": "Nippon Carbon Composites", "country": "Japan", "reliability_score": 98.1},
    {"supplier_id": 4, "supplier_name": "Pacific Precision Castings", "country": "Taiwan", "reliability_score": 88.7},
    {"supplier_id": 5, "supplier_name": "Global Sensors Ltd", "country": "UK", "reliability_score": 95.0},
    {"supplier_id": 6, "supplier_name": "Nordic Electronics Group", "country": "Sweden", "reliability_score": 92.4}
]
df_suppliers = pd.DataFrame(suppliers_data)

# ==========================================
# 2. RAW MATERIALS (8 Core Components)
# ==========================================
raw_materials_data = [
    {"material_id": 1, "material_name": "Titanium Alloy Grade 5", "unit_cost": 450.00},
    {"material_id": 2, "material_name": "Carbon Fiber Prepreg Sheet", "unit_cost": 220.00},
    {"material_id": 3, "material_name": "Micro-Controller Unit (MCU)", "unit_cost": 85.00},
    {"material_id": 4, "material_name": "Industrial Sensor Core", "unit_cost": 45.00},
    {"material_id": 5, "material_name": "High-Temp Thermal Coating", "unit_cost": 115.00},
    {"material_id": 6, "material_name": "Hydraulic Pressure Valve", "unit_cost": 175.00},
    {"material_id": 7, "material_name": "High-Grade Copper Spool", "unit_cost": 90.00},
    {"material_id": 8, "material_name": "Structural Aluminum Plate", "unit_cost": 130.00}
]
df_raw_materials = pd.DataFrame(raw_materials_data)

# Map raw materials to appropriate suppliers
material_supplier_map = {
    1: [1, 2],       # Titanium -> USA, Germany
    2: [3],          # Carbon Fiber -> Japan
    3: [5, 6],       # MCU -> UK, Sweden
    4: [5],          # Sensor Core -> UK
    5: [2, 4],       # Thermal Coating -> Germany, Taiwan
    6: [4, 1],       # Valve -> Taiwan, USA
    7: [1, 2, 4],    # Copper -> USA, Germany, Taiwan
    8: [1, 2]        # Aluminum -> USA, Germany
}

# ==========================================
# 3. INVENTORY LEVELS
# ==========================================
inventory_data = []
inv_id = 1
for _, factory in factories.iterrows():
    for _, mat in df_raw_materials.iterrows():
        inventory_data.append({
            "inventory_id": inv_id,
            "factory_id": int(factory["factory_id"]),
            "material_id": int(mat["material_id"]),
            "quantity_on_hand": random.randint(500, 3000),
            "reorder_point": random.randint(300, 450),
            "safety_stock": 200
        })
        inv_id += 1
df_inventory = pd.DataFrame(inventory_data)

# ==========================================
# 4. PURCHASE ORDERS (Historical orders tracking lead times)
# ==========================================
purchase_orders = []
po_id = 1
start_date = datetime.now() - timedelta(days=730)

for i in range(1200):  # Generating 1,200 PO records over 2 years
    factory = factories.sample(n=1).iloc[0]
    mat = df_raw_materials.sample(n=1).iloc[0]
    possible_suppliers = material_supplier_map[mat["material_id"]]
    supplier_id = random.choice(possible_suppliers)
    
    order_date = start_date + timedelta(days=random.randint(0, 715))
    # Standard lead time is 5-15 days. Add random supplier delay spikes
    lead_days = random.randint(5, 15)
    if random.random() > 0.90:  # 10% chance of supply chain delays
        lead_days += random.randint(7, 20)
        
    delivery_date = order_date + timedelta(days=lead_days)
    qty = random.choice([500, 1000, 1500, 2000])
    
    purchase_orders.append({
        "po_id": po_id,
        "factory_id": int(factory["factory_id"]),
        "supplier_id": supplier_id,
        "material_id": int(mat["material_id"]),
        "quantity_ordered": qty,
        "order_date": order_date.date(),
        "delivered_date": delivery_date.date(),
        "total_cost": round(qty * mat["unit_cost"], 2),
        "status": "Delivered"
    })
    po_id += 1
df_purchase_orders = pd.DataFrame(purchase_orders)
# CONVERSION FIX: Cast dates to string format for safe SQL writing
df_purchase_orders["order_date"] = df_purchase_orders["order_date"].astype(str)
df_purchase_orders["delivered_date"] = df_purchase_orders["delivered_date"].astype(str)

# ==========================================
# 5. QUALITY INSPECTIONS & DEFECT LOGS
# ==========================================
inspections = []
defect_logs = []
insp_id = 1
defect_id = 1

# Extract jobs that had production runs to inspect
# Change random.seed to random_state
sampled_jobs = jobs.sample(frac=0.8, random_state=42) # Inspect 80% of jobs

for _, job in sampled_jobs.iterrows():
    # Inspection results
    has_defects = job["quantity_defective"] > 0
    passed = not has_defects if random.random() < 0.95 else True # Some slip through or pass with caveats
    
    inspections.append({
        "inspection_id": insp_id,
        "job_id": int(job["job_id"]),
        "inspection_date": fake.date_this_decade(),
        "inspected_by": f"Inspector {random.choice(['Alpha', 'Bravo', 'Charlie', 'Delta'])}",
        "result": "Pass" if passed else "Fail",
        "measured_deviation_mm": round(random.uniform(0.01, 0.45), 3) if passed else round(random.uniform(0.50, 2.30), 3)
    })
    
    # If failed, log root cause details (approx 1,500-2,000 records)
    if not passed and has_defects:
        defect_logs.append({
            "defect_log_id": defect_id,
            "inspection_id": insp_id,
            "defect_type": random.choice(["Surface Scratch", "Dimensional Deviation", "Tensile Microcrack", "Thermal Discoloration"]),
            "severity": random.choice(["Minor", "Major", "Critical"]),
            "action_taken": random.choice(["Scrapped", "Reworked", "Returned to Vendor"])
        })
        defect_id += 1
        
    insp_id += 1

df_inspections = pd.DataFrame(inspections)
# CONVERSION FIX: Cast dates to string format for safe SQL writing
df_inspections["inspection_date"] = df_inspections["inspection_date"].astype(str)

df_defect_logs = pd.DataFrame(defect_logs)

# ==========================================
# 6. INJECT FINAL WAVE INTO MYSQL
# ==========================================
print("⚡ Loading supply chain and quality records into MySQL...")
df_suppliers.to_sql("suppliers", con=engine, if_exists="replace", index=False)
df_raw_materials.to_sql("raw_materials", con=engine, if_exists="replace", index=False)
df_inventory.to_sql("inventory_levels", con=engine, if_exists="replace", index=False)
df_purchase_orders.to_sql("purchase_orders", con=engine, if_exists="replace", index=False)
df_inspections.to_sql("quality_inspections", con=engine, if_exists="replace", index=False)
df_defect_logs.to_sql("defect_logs", con=engine, if_exists="replace", index=False)

# Calculate totals
all_tables = ["factories", "production_lines", "machines", "products", "production_jobs", 
              "machine_sensors", "maintenance_logs", "suppliers", "raw_materials", 
              "inventory_levels", "purchase_orders", "quality_inspections", "defect_logs"]

total_db_records = 0
for table in all_tables:
    count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", con=engine).iloc[0]["count"]
    total_db_records += count

print(f"✅ Phase 3 Complete!")
print(f"   - Suppliers Loaded: {len(df_suppliers)}")
print(f"   - Raw Materials Loaded: {len(df_raw_materials)}")
print(f"   - Purchase Orders Loaded: {len(df_purchase_orders)}")
print(f"   - Quality Inspections Loaded: {len(df_inspections)}")
print(f"   - Defect Logs Loaded: {len(df_defect_logs)}")
print(f"\n🏆 CONGRATULATIONS! ForgeIQ database is fully loaded with exactly {len(all_tables)} tables and a grand total of {total_db_records:,} records.")