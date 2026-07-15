import streamlit as st
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.engine import URL
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Set page configuration
st.set_page_config(
    page_title="ForgeIQ - Smart Manufacturing Analytics",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# DATABASE CONNECTION SETUP
# ==========================================
USER = "root"                  # <-- Your MySQL username
PASSWORD = "Your_MYSQL_Password"  # <-- Your working password
HOST = "127.0.0.1"
PORT = 3306
DB_NAME = "forgeiq"       # Keeps using your working database setup

@st.cache_resource
def get_db_engine():
    db_url = URL.create(
        drivername="mysql+pymysql", 
        username=USER, 
        password=PASSWORD, 
        host=HOST, 
        port=PORT, 
        database=DB_NAME
    )
    return sqlalchemy.create_engine(db_url)

try:
    engine = get_db_engine()
except Exception as e:
    st.error(f"Could not connect to database: {e}")

# ==========================================
# HEADER & SIDEBAR BRANDING
# ==========================================
st.title("⚙️ ForgeIQ | Operations & Predictive Maintenance")
st.markdown("---")

st.sidebar.image("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=300&q=80", use_container_width=True)
st.sidebar.title("ForgeIQ Control Center")
st.sidebar.markdown("*Empowering smart factories with predictive intelligence.*")

# Navigation tabs
tab_kpis, tab_predictive, tab_explorer = st.tabs([
    "📊 Factory KPIs & OEE", 
    "🔮 ML Predictive Maintenance", 
    "🗂️ Database Table Explorer"
])

# ==========================================
# TAB 1: FACTORY KPIs & OEE
# ==========================================
with tab_kpis:
    st.subheader("Factory Performance Overview")
    
    # 1. Fetch KPI overview cards
    query_cards = """
    SELECT 
        (SELECT COUNT(*) FROM machines) as total_machines,
        (SELECT SUM(quantity_produced) FROM production_jobs) as total_produced,
        (SELECT SUM(quantity_defective) FROM production_jobs) as total_defects,
        (SELECT COUNT(*) FROM maintenance_logs) as total_maintenance_events
    """
    df_cards = pd.read_sql(query_cards, con=engine)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Assets", f"{df_cards['total_machines'][0]} Machines")
    col2.metric("Total Throughput", f"{df_cards['total_produced'][0]:,} Units")
    
    defect_pct = (df_cards['total_defects'][0] / df_cards['total_produced'][0]) * 100
    col3.metric("Defect Rate", f"{defect_pct:.2f}%", delta=f"{defect_pct - 3.0:.1f}% vs Target", delta_color="inverse")
    col4.metric("Downtime Events", f"{df_cards['total_maintenance_events'][0]} Incidents")

    st.markdown("### Overall Equipment Effectiveness (OEE) Analysis")
    
    # Query OEE Data
    query_oee = """
    SELECT 
        m.machine_name,
        f.location,
        SUM(pj.runtime_hours) as total_runtime,
        SUM(pj.quantity_produced) as total_produced,
        ROUND(((SUM(pj.quantity_produced) - SUM(pj.quantity_defective)) / SUM(pj.quantity_produced)) * 100, 1) as quality_rate
    FROM production_jobs pj
    JOIN machines m ON pj.machine_id = m.machine_id
    JOIN production_lines pl ON m.line_id = pl.line_id
    JOIN factories f ON pl.factory_id = f.factory_id
    GROUP BY m.machine_id, m.machine_name, f.location
    """
    df_oee = pd.read_sql(query_oee, con=engine)
    
    # Simple dropdown filter
    location_filter = st.selectbox("Select Factory Location to Filter Metrics:", ["All Locations"] + list(df_oee['location'].unique()))
    
    if location_filter != "All Locations":
        filtered_df = df_oee[df_oee['location'] == location_filter]
    else:
        filtered_df = df_oee

    # Plotly Bar Chart
    fig_oee = px.bar(
        filtered_df, 
        x='machine_name', 
        y='quality_rate', 
        color='quality_rate',
        color_continuous_scale=px.colors.sequential.Bluered_r,
        title="Quality Rate % by Production Asset",
        labels={'quality_rate': 'Quality Rate (%)', 'machine_name': 'Machine Name'}
    )
    st.plotly_chart(fig_oee, use_container_width=True)

# ==========================================
# TAB 2: MACHINE LEARNING PREDICTIVE MAINTENANCE
# ==========================================
with tab_predictive:
    st.subheader("Machine Learning Early-Warning System")
    st.write("ForgeIQ uses a Random Forest Classifier to assess sensor stream health and predict potential machine failures.")
    
    if st.button("🔄 Retrain and Run Predictor Model"):
        with st.spinner("Analyzing telemetry data..."):
            # Load & process data
            df_sensors = pd.read_sql("SELECT machine_id, timestamp, temperature_c, vibration_mmss, pressure_psi FROM machine_sensors", con=engine)
            df_maint = pd.read_sql("SELECT machine_id, log_date, maintenance_type FROM maintenance_logs WHERE maintenance_type IN ('Unscheduled Breakdown', 'Corrective')", con=engine)
            
            df_sensors['date'] = pd.to_datetime(df_sensors['timestamp']).dt.date
            df_maint['log_date'] = pd.to_datetime(df_maint['log_date']).dt.date
            
            merged = pd.merge(df_sensors, df_maint, left_on=['machine_id', 'date'], right_on=['machine_id', 'log_date'], how='left')
            merged['failed'] = np.where(merged['maintenance_type'].notna(), 1, 0)
            
            X = merged[['temperature_c', 'vibration_mmss', 'pressure_psi']]
            y = merged['failed']
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
            
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Show Metrics
            acc = model.score(X_test, y_test) * 100
            st.success(f"🧠 Model trained successfully with **{acc:.2f}%** validation accuracy!")
            
            # Display Feature Importance
            importances = pd.DataFrame({
                'Sensor Type': ['Temperature (°C)', 'Vibration (mm/s)', 'Pressure (PSI)'],
                'Influence %': model.feature_importances_ * 100
            }).sort_values('Influence %', ascending=False)
            
            fig_importance = px.bar(
                importances, 
                x='Influence %', 
                y='Sensor Type', 
                orientation='h',
                title="Which Sensor Matters Most for Predicting Breakdowns?",
                color='Influence %',
                color_continuous_scale='sunset'
            )
            st.plotly_chart(fig_importance, use_container_width=True)

# ==========================================
# TAB 3: DATABASE EXPLORER
# ==========================================
with tab_explorer:
    st.subheader("Raw Table Explorer")
    st.write("Browse through any of the 13 foundational database tables inside ForgeIQ.")
    
    tables_list = [
        "factories", "production_lines", "machines", "products", 
        "production_jobs", "machine_sensors", "maintenance_logs", 
        "suppliers", "raw_materials", "inventory_levels", 
        "purchase_orders", "quality_inspections", "defect_logs"
    ]
    
    selected_table = st.selectbox("Select a database table to inspect:", tables_list)
    
    # Display table content dynamically
    df_table_preview = pd.read_sql(f"SELECT * FROM {selected_table} LIMIT 100", con=engine)
    st.write(f"Showing up to first 100 records of `{selected_table}`:")
    st.dataframe(df_table_preview, use_container_width=True)