import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "energy_data.csv"
DB_PATH = BASE_DIR / "database" / "energy.db"


def create_indexes(conn=None):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        close_conn = True

    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON energy_consumption(timestamp);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_building_floor_appliance ON energy_consumption(building, floor, appliance);")
    conn.commit()

    if close_conn:
        conn.close()


def create_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)

    conn = sqlite3.connect(DB_PATH)

    df.to_sql(
        "energy_consumption",
        conn,
        if_exists="replace",
        index=False
    )

    create_indexes(conn)
    conn.close()

    print("SQLite database created successfully!")
    print(f"Database: {DB_PATH}")
    print(f"Table: energy_consumption")
    print(f"Rows inserted: {len(df):,}")
    print("Indexes created: idx_timestamp, idx_building_floor_appliance")


def run_query(query):
    conn = sqlite3.connect(DB_PATH)

    result = pd.read_sql_query(query, conn)

    conn.close()

    return result


if __name__ == "__main__":
    create_database()

    # Test SQL query
    query = """
    SELECT
        building,
        ROUND(SUM(energy_kwh), 2) AS total_energy_kwh
    FROM energy_consumption
    GROUP BY building
    ORDER BY total_energy_kwh DESC;
    """

    result = run_query(query)

    print("\nEnergy consumption by building:")
    print(result)