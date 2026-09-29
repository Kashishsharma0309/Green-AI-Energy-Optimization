# 🚀 Quick Setup & Run Guide | NEXUS Energy Intelligence

This guide provides step-by-step instructions for anyone (developers, evaluators, or users) to set up, install, and run the **NEXUS Smart Energy Optimization & Simulation Platform** on **Windows**, **macOS**, or **Linux**.

---

## ⚡ Option 1: 1-Click Launch (Windows)

If you are on Windows, you can use the pre-configured 1-click batch scripts:

1. **Install Dependencies (One-time setup)**:
   - Double-click `setup.bat` (or run `./setup.bat` in PowerShell / Command Prompt).
2. **Launch Application**:
   - Double-click `run.bat` (or run `./run.bat`).
   - This starts the server and automatically opens **`http://localhost:5000`** in your default web browser!

---

## 🛠️ Option 2: Manual Setup & Installation (Any OS)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Kashishsharma0309/Green-AI-Energy-Optimization.git
cd Green-AI-Energy-Optimization
```

---

### Step 2: Set Up a Python Virtual Environment

#### On Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### On Linux / macOS (Terminal):
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

*Required packages include: `flask`, `flask-cors`, `scikit-learn`, `pandas`, `numpy`, `plotly`, `joblib`, `openpyxl`, and `streamlit`.*

---

### Step 4: Verify or Rebuild SQLite Database & ML Model (Optional)

The repository already comes with pre-built database records (`database/energy.db`) and trained models (`models/energy_model.pkl`). 

If you ever wish to re-generate the dataset or retrain the models from scratch:

```bash
# 1. Generate 103,680 synthetic multi-building records:
python src/data_generator.py

# 2. Build and index the SQLite database:
python src/database.py

# 3. Train the Random Forest energy forecasting model:
python src/prediction.py
```

---

### Step 5: Start the Application

To start the full-stack web application with the **Interactive Smart Home Simulator**:

```bash
python server.py
```

Now open your web browser and navigate to:
👉 **`http://localhost:5000`**

*(If port 5000 is occupied on your machine, you can change it with: `PORT=5050 python server.py`)*

---

## 🎮 How to Test Key Features in the App

Once the web application is open at **`http://localhost:5000`**:

1. **🏡 Smart Home Simulator (`/`)**:
   - Flip appliance toggles (AC, Smart TV, Dishwasher, EV Charger, Induction Oven).
   - Adjust thermostat setpoints and time-of-day clock.
   - Click the **"🤖 AI Eco-Optimize & Balance"** button to watch the AI automatically resolve energy leaks and show your instant cost savings!
2. **📊 Command Center**:
   - View real-time 72-hour load streams, appliance load shares, and 30-day daily aggregated demand.
3. **🧠 AI Forecasting**:
   - Inspect model accuracy metrics ($R^2$, MAE, RMSE) and 48-hour forward demand curves.
   - Use the **What-If Scenario Sandbox** sliders to test HVAC thermostat offsets and rooftop solar offsets.
4. **🚨 Anomaly Matrix**:
   - Review automatically detected anomalies categorized into Critical, High, and Medium with root-cause diagnoses.
5. **💡 Recommendations**:
   - Explore priority-ranked energy efficiency directives and click **"Apply Action"**.
6. **📁 Data Studio**:
   - Drag and drop [`data/sample_test_energy_data.csv`](data/sample_test_energy_data.csv) or [`data/sample_test_energy_data.xlsx`](data/sample_test_energy_data.xlsx) into the uploader to test custom data ingestion.
7. **📄 Monthly Reports**:
   - View executive energy audit summaries and click **"Export"** for printable statements.

---

## ❓ Frequently Asked Questions (FAQ)

#### Q: How do I stop the running server?
Press `Ctrl + C` in the terminal / command prompt where `python server.py` is running.

#### Q: Can I also run the classic Streamlit dashboard?
Yes! Simply run:
```bash
streamlit run app.py
```
And open **`http://localhost:8501`** in your browser. *(Press `Enter` if prompted for an email address to skip it)*.
