# ForgeIQ
# ⚙️ ForgeIQ | Smart Manufacturing Analytics & Predictive Maintenance

ForgeIQ is an end-to-end data engineering and predictive analytics platform built to optimize smart factory operations. This project centralizes siloed operational data into a unified relational database, performs advanced SQL analytics (like OEE tracking), and trains an early-warning Machine Learning model to predict machinery failure using high-frequency IoT sensor telemetry.

![Streamlit Dashboard](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Database](https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![ML](https://img.shields.io/badge/Machine_Learning-Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

---

## 🚀 Key Features

* **Robust Data Simulation Pipeline:** Generates over 29,000 highly realistic records representing factory runs, maintenance logs, and high-frequency IoT sensor streams (vibration, temperature, pressure).
* **Enterprise-Grade MySQL Schema:** Implements a normalized, 13-table relational schema covering suppliers, inventories, production lines, quality assurance logs, and IoT telemetry.
* **Interactive Operations Dashboard:** Built with Streamlit and Plotly to enable search capabilities, real-time KPI card generation, and interactive data filtering.
* **Predictive Maintenance Model:** Trains a Random Forest Classifier to identify impending machine breakdowns based on sensor anomalies with **97.2% validation accuracy**.

---

## 🏗️ System Architecture
[ Python Data Generator ] ──> [ ETL Pipeline (Pandas / SQLAlchemy) ]
│
▼
[ MySQL Relational Database ]
(13 Tables, 29k+ Records)
│
┌───────────────────────┴───────────────────────┐
▼                                               ▼
[ SQL Analytics Engine ]                        [ Machine Learning Pipeline ]
(CTEs, Window Functions, OEE)                     (Random Forest Classification)
│                                               │
└───────────────────────┬───────────────────────┘
▼
[ Streamlit Web Dashboard ]

---

## 📊 Analytical Highlights (SQL Queries)

### 1. Overall Equipment Effectiveness (OEE)
We utilize multi-layered CTEs to calculate OEE per physical asset by combining raw runtime hours, throughput volumes, and defective counts:
$$\text{OEE} \approx \text{Availability} \times \text{Performance} \times \text{Quality}$$

### 2. Predictive Maintenance Lead Signal
Utilizes `LAG()` window functions to detect sudden physical spikes (e.g., temperature jumps $\ge 10^\circ\text{C}$ compared to the previous timestamp) to trigger proactive maintenance cycles.

---

## 🧠 Machine Learning Insights
The Random Forest Classifier evaluates physical sensor inputs to predict breakdowns. The feature importance analysis reveals the primary root causes of mechanical failures in our factories:
* 🌡️ **Temperature:** 37.4% influence (Overheating motors)
* 💨 **Pressure:** 35.2% influence (Hydraulic or pneumatic pressure drops)
* 📳 **Vibration:** 27.5% influence (Mechanical wear, belt slippage, or misalignment)

---

## 💻 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/ForgeIQ.git](https://github.com/YOUR_USERNAME/ForgeIQ.git)
   cd ForgeIQ

   Install Dependencies:

Bash
pip install pandas numpy sqlalchemy pymysql scikit-learn streamlit plotly
Populate the Database:

Bash
python generate_operations.py
python generate_supply_chain.py
Launch the Web Dashboard:

Bash
streamlit run app.py

---

## 📤 Step 3: Push to GitHub

1. Go to [GitHub](https://github.com/) and click the green **New** button to create a repository.
2. Name it **`ForgeIQ`**, leave it public, and **do not** check "Add a README file" or "Add .gitignore" (since we just created them locally). Click **Create repository**.
3. Open your PowerShell terminal (`C:\Users\tfbpt\OneDrive\Desktop\MDP`) and run these commands:

```bash
# Initialize git in your folder
git init

# Add all of your files to the staging area
git add .

# Commit your files
git commit -m "Initial commit: ForgeIQ Smart Factory Platform"

# Link your local folder to your online GitHub repository
git branch -M main
git remote add origin https://github.com/AbhiramVedavyas/ForgeIQ.git

# Push the code!
git push -u origin main
