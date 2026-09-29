import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "energy.db"


def load_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        timestamp,
        building,
        floor,
        appliance,
        temperature_c,
        humidity_percent,
        occupancy,
        power_kw,
        energy_kwh
    FROM energy_consumption
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def detect_anomalies(df=None, contamination=0.02):
    if df is None:
        df = load_data()

    if df.empty:
        return df.copy()

    features = [
        "temperature_c",
        "humidity_percent",
        "occupancy",
        "power_kw",
        "energy_kwh",
    ]

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )

    result = df.copy()
    result["anomaly_label"] = model.fit_predict(result[features])
    result["anomaly_score"] = -model.decision_function(result[features])

    result["anomaly"] = result["anomaly_label"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    anomalies = (
        result[result["anomaly"] == "Anomaly"]
        .sort_values("energy_kwh", ascending=False)
    )

    print("Anomaly detection completed successfully!")
    print(f"Total records: {len(result):,}")
    print(f"Anomalies detected: {len(anomalies):,}")

    if not anomalies.empty:
        print("\nTop abnormal energy consumption records:")
        print(
            anomalies[
                [
                    "timestamp",
                    "building",
                    "floor",
                    "appliance",
                    "power_kw",
                    "energy_kwh",
                    "anomaly",
                ]
            ].head(10).to_string(index=False)
        )

    return result


if __name__ == "__main__":
    detect_anomalies()