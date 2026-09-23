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


def detect_anomalies():
    df = load_data()

    features = [
        "temperature_c",
        "humidity_percent",
        "occupancy",
        "power_kw",
        "energy_kwh",
    ]

    model = IsolationForest(
        contamination=0.02,
        random_state=42,
        n_estimators=100,
    )

    df["anomaly_score"] = model.fit_predict(df[features])

    df["anomaly"] = df["anomaly_score"].map({
        1: "Normal",
        -1: "Anomaly"
    })

    anomalies = (
        df[df["anomaly"] == "Anomaly"]
        .sort_values("energy_kwh", ascending=False)
    )

    print("Anomaly detection completed successfully!")
    print(f"Total records: {len(df):,}")
    print(f"Anomalies detected: {len(anomalies):,}")

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

    return df


if __name__ == "__main__":
    detect_anomalies()