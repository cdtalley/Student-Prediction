"""
Load student prediction CSV data into SQLite for Superset dashboards.
Run: python scripts/load_data_for_superset.py
"""
import sqlite3
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = PROJECT_ROOT / "superset_data" / "student_prediction.db"


def load_tables():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Retention data - add period_date for Superset datetime charts (semester -> first-of-term date)
    if (DATA_DIR / "retention_data.csv").exists():
        df = pd.read_csv(DATA_DIR / "retention_data.csv")
        semester_dates = {1: "2022-01-01", 2: "2022-05-01", 3: "2022-09-01", 4: "2023-01-01"}
        df["period_date"] = pd.to_datetime(df["semester"].map(semester_dates).fillna("2022-01-01"))
        df.to_sql("retention", conn, if_exists="replace", index=False)
        print(f"Loaded retention: {len(df)} rows")

    # Lead scoring - add period_date for Superset (synthetic created date)
    for name, f in [
        ("ga4", "ga4_data.csv"),
        ("crm", "crm_data.csv"),
        ("sis", "sis_data.csv"),
    ]:
        path = DATA_DIR / f
        if path.exists():
            df = pd.read_csv(path)
            # Add period_date so datasets have a datetime column (required by some chart types)
            df["period_date"] = pd.to_datetime("2023-01-01")
            df.to_sql(name, conn, if_exists="replace", index=False)
            print(f"Loaded {name}: {len(df)} rows")

    conn.close()
    print(f"\nDatabase: {DB_PATH}")
    print("In Superset: Data > Databases > + Database > SQLite")
    print("Superset connection: sqlite:////app/superset_data/student_prediction.db")


if __name__ == "__main__":
    if not DATA_DIR.exists():
        print("Run python src/train.py first to generate data.")
        exit(1)
    load_tables()
