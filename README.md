# NEXUS | Green AI Energy Optimization & Smart Simulator ◈

[![Python](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Chart.js](https://img.shields.io/badge/Frontend-Vanilla%20CSS%20%2B%20Chart.js-FF6384?logo=chartdotjs&logoColor=white)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-MIT-00E5A3)](#-license)

> An end-to-end Smart Energy Management & Simulation Platform combining Machine Learning, thermodynamic calculations, and an interactive 2D Smart Estate Simulator to monitor, predict, diagnose, and optimize electricity consumption.

---

## 📌 Table of Contents

- [Overview & Problem Statement](#-overview--problem-statement)
- [Key Features](#-key-features)
- [Interactive Smart Estate Simulator](#-interactive-smart-estate-simulator)
- [System Architecture & Directory Structure](#-system-architecture--directory-structure)
- [Machine Learning & Mathematical Logics](#-machine-learning--mathematical-logics)
- [Technology Stack](#-technology-stack)
- [Getting Started & Installation](#-getting-started--installation)
- [Running the Application](#-running-the-application)
- [REST API Reference](#-rest-api-reference)
- [Testing & Data Studio](#-testing--data-studio)
- [License](#-license)

---

## 🎯 Overview & Problem Statement

Modern facilities, campuses, and residential buildings waste between **15% and 35%** of their total electricity due to inefficient HVAC thermostat setpoints, phantom standby loads during vacant hours, unoptimized time-of-use tariff draws, and unmonitored equipment degradation faults.

**NEXUS** solves this with an integrated AI-driven intelligence suite:
1. **Real-Time Monitoring**: Ingests sensor metrics across facilities, floors, and appliances.
2. **Predictive Consumption Modeling**: Multi-variable ML regression forecasting hourly energy demand 48 hours ahead.
3. **Unsupervised Anomaly Detection**: Isolation Forests identifying spikes, power surges, and ghost loads with root-cause diagnostics.
4. **Interactive Energy Simulator**: A gamified, visual digital twin of living spaces allowing real-time appliance control, solar generation balancing, and 1-click **AI Eco-Optimization**.
5. **Data Studio & Ingestion**: Drag-and-drop CSV / Excel data ingestion with automatic schema validation.

---

## ✨ Key Features

| Capability | Description |
| :--- | :--- |
| 🏡 **Smart Home Simulator** | Interactive 2D/Isometric blueprint with living room, kitchen, bedroom, office, EV garage, and solar PV roof. |
| 🤖 **AI Eco-Optimizer** | 1-Click auto-balancing engine that tunes thermostats to 24°C, cuts vacant zone loads, and shifts peak EV charging. |
| 📈 **Command Center** | 72-hour live telemetry stream, appliance category donuts, and 30-day daily aggregated demand trends. |
| 🧠 **AI Forecasting Sandbox** | Random Forest Regressor ($R^2 = 0.9885$) with interactive What-If scenario sliders for temperature setpoints & solar capacity. |
| 🚨 **Anomaly Matrix** | Categorizes events into Critical, High, and Medium with automated root-cause explanations. |
| 💡 **Smart Directives & ROI** | Priority-ranked recommendations with quantified monthly monetary (₹) and energy (kWh) savings. |
| 📁 **Data Studio** | CSV and Excel (`.xlsx`, `.xls`) file uploader with automatic column mapping and instant model retraining. |
| 📄 **Monthly Reports** | Executive billing statements with peak demand intensity, cost summaries, and printable report export. |

---

## 🏡 Interactive Smart Estate Simulator

The simulator provides an interactive digital twin of a smart residence/facility:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ☀️ ROOFTOP SOLAR PV (6.5 kWp)                     │
│  Live Solar Gen: 4.85 kW   │   Battery Storage: 7.8/10.0 kWh (78%)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    ▼
┌───────────────────┬───────────────────┬───────────────────┐
│ 🛋️ Living Room    │ 🍳 Modern Kitchen  │ 🛏️ Master Suite   │
│ - Dual-Inverter AC│ - Smart Fridge    │ - Quiet Split AC  │
│ - 75" 4K OLED TV  │ - Induction Oven  │ - True HEPA Filter│
│ - LED Chandelier  │ - Eco Dishwasher  │ - Bedside Lights  │
├───────────────────┼───────────────────┴───────────────────┤
│ 🖥️ Tech Office    │ 🚗 Utility & Garage                   │
│ - AI Workstation  │ - 7.4 kW Level-2 Smart EV Charger     │
│ - Mini-Split AC   │ - Hybrid Heat Pump Water Heater       │
└───────────────────┴───────────────────────────────────────┘
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        ⚡ LIVE TELEMETRY GAUGES                        │
│ Total Load: 4.85 kW  │ Net Grid: 0.00 kW (Net Zero) │ Tariff: ₹7.50/hr │
└────────────────────────────────────────────────────────────────────────┘
```

### Simulator Capabilities:
- **Appliance Controls**: Toggle ON/OFF switches, adjust AC thermostats (16°C – 30°C), dim light intensity (10% – 100%), and set EV charging rates (1.4 kW – 7.4 kW).
- **Occupancy & Weather**: Toggle room occupancy (Occupied / Vacant) and adjust outdoor temperature (15°C – 44°C) or diurnal time of day (0:00 – 23:00).
- **AI Auto-Balancing**: Running the AI Eco-Optimizer executes automated thermodynamic rules, removes ghost standby loads, and displays an animated Before vs. After savings breakdown.

---

## 🏗️ System Architecture & Directory Structure

```
Green-AI-Energy-Optimization/
│
├── backend/                      # 🐍 Backend REST API & Server Services
│   ├── __init__.py
│   ├── api.py                   # Flask Blueprint, REST endpoints, in-memory caching & controllers
│   └── server.py                # Standalone backend server launcher
│
├── frontend/                     # 🌐 Web Client Assets (Cyber-Emerald Glassmorphism)
│   ├── index.html               # Master Single-Page Application (SPA)
│   ├── css/
│   │   └── style.css            # Custom design system, micro-animations, glass cards & telemetry
│   └── js/
│       ├── app.js               # Navigation routing, Chart.js telemetry & Data Studio
│       └── simulator.js         # Interactive Smart Estate simulator engine
│
├── src/                          # 🧠 Machine Learning & Data Processing Pipelines
│   ├── __init__.py
│   ├── anomaly_detection.py     # Isolation Forest unsupervised anomaly detector
│   ├── data_generator.py        # Multi-building synthetic dataset generator
│   ├── database.py              # SQLite connection, schema, and query helpers
│   ├── prediction.py            # Random Forest regression & What-If scenario logic
│   └── recommendations.py       # Rule-based & AI energy-saving optimization engine
│
├── data/                         # 📊 Dataset storage
│   ├── energy_data.csv          # Historical primary dataset (103,680 records)
│   ├── sample_test_energy_data.csv   # Custom sample test dataset
│   └── sample_test_energy_data.xlsx  # Custom sample test Excel sheet
│
├── database/                     # 🗄️ SQLite database storage
│   └── energy.db
│
├── models/                       # 🤖 Saved ML model artifacts
│   └── energy_model.pkl
│
├── server.py                     # 🚀 Main entry point to launch the Full-Stack Web App
├── app.py                        # 📊 Streamlit dashboard entry point (Classic view)
├── requirements.txt              # 📦 Python dependencies
└── README.md                     # 📖 Documentation & architecture guide
```

---

## 🧠 Machine Learning & Mathematical Logics

### 1. Demand Forecasting Regression
The forecasting model employs an ensemble `RandomForestRegressor` ($N_{trees} = 150$, $depth_{max} = 15$) trained on historical time-series sequences.

$$\text{Energy}_{t} = f(\text{Temp}_t, \text{Humidity}_t, \text{Occupancy}_t, \text{Hour}_t, \text{DayOfWeek}_t, \text{Month}_t, \text{Energy}_{t-1}, \text{Energy}_{t-24})$$

- **Lagged Features**: $\text{Energy}_{t-1}$ (immediate previous hour) and $\text{Energy}_{t-24}$ (same hour previous day) capture inertia and daily diurnal seasonality.
- **Model Evaluation**:
  - $R^2 = 0.9885$
  - $\text{MAE} = 1.3672\text{ kWh}$
  - $\text{RMSE} = 2.1240\text{ kWh}$

### 2. Thermodynamic AC Power Scaling
Cooling load power in the simulator scales dynamically with the outdoor-indoor temperature differential:

$$P_{\text{AC}} = P_{\text{base}} \cdot \left( 0.65 + \max(0, T_{\text{outdoor}} - T_{\text{setpoint}}) \cdot 0.16 \right)$$

*Every $1^\circ\text{C}$ reduction below $24^\circ\text{C}$ exponentially increases chiller energy demand by $\sim 6\%$.*

### 3. Isolation Forest Anomaly Detection
Multi-dimensional Isolation Forest builds an ensemble of $100$ isolation trees over the feature space $(\text{Temp}, \text{Humidity}, \text{Occupancy}, \text{Power}, \text{Energy})$.

- An anomaly score $s(x, n) = 2^{-\frac{E(h(x))}{c(n)}}$ is evaluated.
- Records in the top contamination threshold ($2\%$) are flagged and classified into **Critical** ($\ge 90\text{th percentile}$ score), **High** ($\ge 75\text{th percentile}$), and **Medium**.

### 4. Solar PV Generation & Net Zero Math
Solar generation curves follow a half-sine diurnal path between 06:00 and 18:00:

$$P_{\text{solar}}(t) = \max\left(0, P_{\text{capacity}} \cdot \sin\left(\frac{(t - 6)\pi}{12}\right)\right)$$

$$\text{Net Grid Import} = \max(0, P_{\text{load}} - P_{\text{solar}})$$

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend UI** | HTML5, Vanilla CSS3 (Cyber-Emerald & Slate Glassmorphism), JavaScript (ES6+), Google Fonts (`Plus Jakarta Sans`, `DM Mono`) |
| **Visualizations** | [Chart.js](https://www.chartjs.org/) (Real-time telemetry, actual vs. predicted curves, anomaly distribution, daily bars) |
| **Backend Framework** | [Flask 3.1](https://flask.palletsprojects.com/), Flask-CORS |
| **Machine Learning** | [Scikit-learn](https://scikit-learn.org/) (`RandomForestRegressor`, `IsolationForest`), [Joblib](https://joblib.readthedocs.io/) |
| **Data Processing** | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), [OpenPyXL](https://openpyxl.readthedocs.io/) |
| **Database** | [SQLite3](https://www.sqlite.org/) |

---

## 🚀 Getting Started & Installation

### 1. Clone Repository
```powershell
git clone https://github.com/Kashishsharma0309/Green-AI-Energy-Optimization.git
cd Green-AI-Energy-Optimization
```

### 2. Set Up Python Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Activate on Linux / macOS
source venv/bin/activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 💻 Running the Application

### Option A: Modern Full-Stack Web App (Recommended)
Launches the full interactive Smart Home Simulator, Machine Learning Analytics, and Data Studio:
```powershell
python server.py
```
👉 Open your browser at: **`http://localhost:5000`**

---

### Option B: Streamlit Dashboard (Classic)
```powershell
streamlit run app.py
```
👉 Open your browser at: **`http://localhost:8501`** *(Press Enter if prompted for email)*

---

## 🌐 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/overview` | Returns aggregate metrics (kWh, ₹, CO₂), peak hours, building/appliance summaries, and 30-day daily trends. |
| `GET` | `/api/live-stream` | Returns the recent 72-hour telemetry stream and instantaneous load snapshot. |
| `GET` | `/api/predict` | Computes model evaluation scores ($R^2$, MAE, RMSE), feature weights, and 48-hour forward demand curve. |
| `POST` | `/api/predict/what-if` | Simulates What-If scenarios for thermostat setpoints, load shedding %, and solar capacity offsets. |
| `GET` | `/api/anomalies` | Runs Isolation Forest detection and returns categorized severity counts, appliance distributions, and fault logs. |
| `GET` | `/api/recommendations` | Returns rule-based and AI optimization directives with quantified monthly monetary and energy savings. |
| `POST` | `/api/simulator/audit` | Audits real-time appliance states in the simulator and identifies active energy leaks. |
| `POST` | `/api/upload` | Ingests CSV or Excel (`.xlsx`, `.xls`) datasets into the SQLite database and triggers model retraining. |
| `GET` | `/api/reports/monthly` | Returns monthly energy statements, peak demands, and energy intensity indices. |

---

## 🧪 Testing & Data Studio

You can test individual pipeline modules from the command line:

```powershell
# 1. Regenerate synthetic multi-building time series
python src/data_generator.py

# 2. Rebuild and index SQLite database
python src/database.py

# 3. Retrain Random Forest regression model
python src/prediction.py

# 4. Run Isolation Forest anomaly detection
python src/anomaly_detection.py

# 5. Generate energy-saving recommendations
python src/recommendations.py
```

### Testing Custom File Ingestion:
Sample datasets are pre-packaged in the `data/` directory:
- [`data/sample_test_energy_data.csv`](data/sample_test_energy_data.csv)
- [`data/sample_test_energy_data.xlsx`](data/sample_test_energy_data.xlsx)

To test, go to **📁 Data Studio & CSV** in the web application (`http://localhost:5000`), upload either file, and select **Append** or **Replace**.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
