# NEXUS | Green AI Energy Optimization ◈

Smart Building Intelligence platform leveraging Machine Learning to monitor, predict, and optimize building energy consumption.

---

## 📌 Overview

**NEXUS** is an AI-powered energy management and optimization dashboard designed for commercial and institutional smart buildings. By analyzing sensor metrics such as occupancy, outdoor temperature, and humidity, NEXUS provides actionable insights to minimize carbon footprint and lower utility costs.

### Key Capabilities:
- **Real-Time Energy Monitoring**: Interactive visualizations across multiple buildings, floors, and appliances.
- **Predictive Consumption Modeling**: ML regression models forecasting hourly energy usage.
- **Anomaly Detection**: Unsupervised Isolation Forest algorithms detecting abnormal consumption spikes and equipment faults.
- **Smart Recommendations**: Rule-based and AI-driven recommendations for peak shaving and efficiency optimizations.
- **SQL Analytics Engine**: Integrated SQLite database querying and reports generation.

---

## 🏗️ Architecture

```
Green-AI-Energy-Optimization/
│
├── .streamlit/             # Streamlit configuration and themes
├── assets/                 # Static visual assets
├── data/                   # Synthetic and historical energy datasets
│   └── energy_data.csv
├── database/               # SQLite database storage
│   └── energy.db
├── models/                 # Pretrained machine learning models
│   └── energy_model.pkl
├── reports/                # Exported reports and logs
├── src/                    # Core application logic
│   ├── anomaly_detection.py# Isolation Forest anomaly detector
│   ├── database.py         # SQLite connection and migration helpers
│   ├── data_generator.py   # Multi-building synthetic data generator
│   ├── prediction.py       # ML training and prediction pipelines
│   └── recommendations.py  # Optimization & energy-saving algorithms
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ (Python 3.10+ recommended)
- `git`

### 2. Installation

Clone the repository:
```bash
git clone https://github.com/Kashishsharma0309/Green-AI-Energy-Optimization.git
cd Green-AI-Energy-Optimization
```

Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Application

Launch the Streamlit dashboard:
```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`.

---

## 🛠️ Tech Stack

- **Frontend / Dashboard**: [Streamlit](https://streamlit.io/)
- **Data Manipulation**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Machine Learning**: [Scikit-learn](https://scikit-learn.org/), [Joblib](https://joblib.readthedocs.io/)
- **Visualizations**: [Plotly](https://plotly.com/)
- **Database**: [SQLite3](https://www.sqlite.org/)

---

## 📄 License

This project is licensed under the MIT License.
