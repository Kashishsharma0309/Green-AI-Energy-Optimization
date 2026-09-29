import sqlite3
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "energy.db"
MODEL_PATH = BASE_DIR / "models" / "energy_model.pkl"


def load_data():
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        timestamp,
        temperature_c,
        humidity_percent,
        occupancy,
        energy_kwh
    FROM energy_consumption
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def prepare_data():
    df = load_data()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Aggregate all appliances into hourly building-level consumption
    hourly = (
        df.groupby("timestamp")
        .agg(
            temperature_c=("temperature_c", "mean"),
            humidity_percent=("humidity_percent", "mean"),
            occupancy=("occupancy", "mean"),
            energy_kwh=("energy_kwh", "sum"),
        )
        .reset_index()
        .sort_values("timestamp")
    )

    # Time features
    hourly["hour"] = hourly["timestamp"].dt.hour
    hourly["day_of_week"] = hourly["timestamp"].dt.dayofweek
    hourly["month"] = hourly["timestamp"].dt.month

    # Previous energy consumption
    hourly["previous_energy"] = hourly["energy_kwh"].shift(1)
    hourly["energy_24h_ago"] = hourly["energy_kwh"].shift(24)

    hourly = hourly.dropna().reset_index(drop=True)

    return hourly


def train_model():
    df = prepare_data()

    features = [
        "temperature_c",
        "humidity_percent",
        "occupancy",
        "hour",
        "day_of_week",
        "month",
        "previous_energy",
        "energy_24h_ago",
    ]

    target = "energy_kwh"

    X = df[features]
    y = df[target]

    # Chronological split — past data for training, future data for testing
    split_index = int(len(df) * 0.8)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]

    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=15,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Improved energy prediction model trained successfully!")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Training rows: {len(X_train):,}")
    print(f"Testing rows: {len(X_test):,}")
    print(f"Mean Absolute Error: {mae:.4f} kWh")
    print(f"R² Score: {r2:.4f}")


FEATURE_NAMES = [
    "temperature_c",
    "humidity_percent",
    "occupancy",
    "hour",
    "day_of_week",
    "month",
    "previous_energy",
    "energy_24h_ago",
]


def get_feature_importances(model):
    """Extract and rank model feature importances."""
    if model is None or not hasattr(model, "feature_importances_"):
        return pd.DataFrame()

    df_imp = pd.DataFrame({
        "Feature": [
            "Outdoor Temperature (°C)",
            "Humidity (%)",
            "Occupancy (people)",
            "Hour of Day",
            "Day of Week",
            "Month",
            "Previous Hour Energy",
            "Energy 24h Ago"
        ],
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=True)

    return df_imp


def simulate_what_if_scenario(model, hourly_df, temp_delta_c=0.0, occupancy_pct_reduction=0.0):
    """Simulate next 24-hour demand with adjusted HVAC temperature setpoint or occupancy setback."""
    if model is None or hourly_df.empty or len(hourly_df) < 24:
        return pd.DataFrame()

    features = FEATURE_NAMES
    latest = hourly_df.iloc[-1].copy()

    # Baseline 24-hour prediction
    baseline_rows = []
    curr_base = latest.copy()
    for step in range(1, 25):
        stamp = curr_base["timestamp"] + pd.Timedelta(hours=step)
        row = curr_base.copy()
        row["timestamp"] = stamp
        row["hour"] = stamp.hour
        row["day_of_week"] = stamp.dayofweek
        row["month"] = stamp.month
        row["previous_energy"] = curr_base["energy_kwh"]
        row["energy_24h_ago"] = hourly_df.iloc[max(0, len(hourly_df) - 24 + step - 1)]["energy_kwh"]

        pred = model.predict(pd.DataFrame([row])[features])[0]
        row["energy_kwh"] = pred
        curr_base = row
        baseline_rows.append(row)

    df_baseline = pd.DataFrame(baseline_rows)

    # Modified scenario prediction
    scenario_rows = []
    curr_scen = latest.copy()
    for step in range(1, 25):
        stamp = curr_scen["timestamp"] + pd.Timedelta(hours=step)
        row = curr_scen.copy()
        row["timestamp"] = stamp
        row["hour"] = stamp.hour
        row["day_of_week"] = stamp.dayofweek
        row["month"] = stamp.month
        row["temperature_c"] = max(10, row["temperature_c"] - temp_delta_c)
        row["occupancy"] = max(0, row["occupancy"] * (1.0 - occupancy_pct_reduction / 100.0))
        row["previous_energy"] = curr_scen["energy_kwh"]
        row["energy_24h_ago"] = hourly_df.iloc[max(0, len(hourly_df) - 24 + step - 1)]["energy_kwh"]

        pred = model.predict(pd.DataFrame([row])[features])[0]
        row["energy_kwh"] = pred
        curr_scen = row
        scenario_rows.append(row)

    df_scenario = pd.DataFrame(scenario_rows)

    combined = pd.DataFrame({
        "timestamp": df_baseline["timestamp"],
        "Baseline Forecast (kWh)": df_baseline["energy_kwh"],
        "Optimized Forecast (kWh)": df_scenario["energy_kwh"],
        "Savings (kWh)": df_baseline["energy_kwh"] - df_scenario["energy_kwh"]
    })

    return combined


if __name__ == "__main__":
    train_model()