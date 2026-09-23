import sqlite3
from pathlib import Path

import pandas as pd

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
        occupancy,
        power_kw,
        energy_kwh
    FROM energy_consumption
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    return df


def generate_recommendations():
    df = load_data()

    recommendations = []

    # Appliance-level average consumption
    appliance_usage = (
        df.groupby("appliance")["energy_kwh"]
        .mean()
        .sort_values(ascending=False)
    )

    overall_average = df["energy_kwh"].mean()

    for appliance, avg_usage in appliance_usage.items():

        if avg_usage > overall_average * 1.5:
            recommendations.append({
                "appliance": appliance,
                "priority": "High",
                "recommendation": (
                    f"{appliance} is consuming significantly more energy "
                    "than the overall average. Review its operating schedule "
                    "and optimize usage."
                )
            })

    # Low occupancy + high consumption
    low_occupancy_high_usage = df[
        (df["occupancy"] < 15) &
        (df["energy_kwh"] > df["energy_kwh"].quantile(0.90))
    ]

    if len(low_occupancy_high_usage) > 0:
        recommendations.append({
            "appliance": "Building Systems",
            "priority": "High",
            "recommendation": (
                "High energy consumption was detected during low-occupancy "
                "periods. Consider automatically reducing HVAC and lighting "
                "when fewer people are present."
            )
        })

    # HVAC recommendation
    hvac_data = df[df["appliance"] == "HVAC"]

    if not hvac_data.empty:
        high_hvac = hvac_data[
            hvac_data["energy_kwh"] > hvac_data["energy_kwh"].quantile(0.90)
        ]

        if len(high_hvac) > 0:
            recommendations.append({
                "appliance": "HVAC",
                "priority": "Medium",
                "recommendation": (
                    "HVAC consumption is high during some periods. "
                    "Optimize temperature settings and reduce HVAC usage "
                    "during low-occupancy hours."
                )
            })

    # Lighting recommendation
    lighting_data = df[df["appliance"] == "Lighting"]

    if not lighting_data.empty:
        unnecessary_lighting = lighting_data[
            (lighting_data["occupancy"] < 10) &
            (lighting_data["energy_kwh"] > lighting_data["energy_kwh"].median())
        ]

        if len(unnecessary_lighting) > 0:
            recommendations.append({
                "appliance": "Lighting",
                "priority": "Medium",
                "recommendation": (
                    "Lighting consumption is relatively high in low-occupancy "
                    "periods. Consider motion sensors or automatic lighting controls."
                )
            })

    result = pd.DataFrame(recommendations)

    print("Energy-saving recommendations generated successfully!")

    if result.empty:
        print("No major energy-saving recommendations found.")
    else:
        print("\nRecommendations:")
        print(result.to_string(index=False))

    return result


if __name__ == "__main__":
    generate_recommendations()