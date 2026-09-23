import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

# Smart building configuration
buildings = {
    "Building A": ["Floor 1", "Floor 2", "Floor 3"],
    "Building B": ["Floor 1", "Floor 2", "Floor 3"],
    "Building C": ["Floor 1", "Floor 2"],
}

appliances = {
    "AC": 2.5,
    "Lighting": 0.4,
    "Computer": 0.25,
    "Printer": 0.15,
    "Refrigerator": 0.5,
    "HVAC": 4.0,
}

timestamps = pd.date_range(
    start="2026-01-01",
    end="2026-03-31 23:00:00",
    freq="h"
)

records = []

for timestamp in timestamps:
    hour = timestamp.hour
    weekday = timestamp.weekday()

    # Occupancy pattern
    if weekday < 5 and 9 <= hour <= 18:
        occupancy = np.random.randint(35, 101)
    elif weekday < 5 and 7 <= hour <= 20:
        occupancy = np.random.randint(10, 50)
    else:
        occupancy = np.random.randint(0, 15)

    # Outdoor temperature pattern
    temperature = (
        24
        + 7 * np.sin((hour - 8) * np.pi / 12)
        + np.random.normal(0, 1.5)
    )

    humidity = np.clip(
        65 - (temperature - 24) * 1.5 + np.random.normal(0, 4),
        30,
        90
    )

    for building, floors in buildings.items():
        for floor in floors:
            for appliance, base_power in appliances.items():

                # Appliance-specific behaviour
                if appliance == "AC":
                    usage_factor = 1.2 if temperature > 28 else 0.7
                    usage_factor *= (0.4 + occupancy / 100)

                elif appliance == "HVAC":
                    usage_factor = 1.0 if occupancy > 20 else 0.35

                elif appliance == "Lighting":
                    usage_factor = (
                        1.0 if 7 <= hour <= 19 else 0.2
                    )
                    usage_factor *= (0.3 + occupancy / 100)

                elif appliance == "Computer":
                    usage_factor = (
                        0.9 if 9 <= hour <= 18 and weekday < 5
                        else 0.15
                    )

                elif appliance == "Printer":
                    usage_factor = (
                        0.8 if 9 <= hour <= 18 and weekday < 5
                        else 0.1
                    )

                else:
                    usage_factor = 0.7

                power = base_power * usage_factor

                # Random variation
                power *= np.random.uniform(0.85, 1.15)

                # Occasional abnormal high consumption
                if np.random.random() < 0.015:
                    power *= np.random.uniform(1.8, 3.0)

                energy_kwh = power * 1  # one-hour interval

                electricity_cost = energy_kwh * 8.0

                co2_kg = energy_kwh * 0.82

                records.append({
                    "timestamp": timestamp,
                    "building": building,
                    "floor": floor,
                    "appliance": appliance,
                    "temperature_c": round(temperature, 2),
                    "humidity_percent": round(humidity, 2),
                    "occupancy": occupancy,
                    "power_kw": round(power, 3),
                    "energy_kwh": round(energy_kwh, 3),
                    "electricity_cost_inr": round(electricity_cost, 2),
                    "co2_kg": round(co2_kg, 3),
                })

df = pd.DataFrame(records)

# Save dataset
output_path = Path(__file__).resolve().parent.parent / "data" / "energy_data.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(output_path, index=False)

print(f"Dataset generated successfully!")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")
print(f"Saved to: {output_path}")
print("\nFirst 5 rows:")
print(df.head())