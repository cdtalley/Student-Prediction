"""
Unified data loader: local CSV (default) or BigQuery.
Set DATA_SOURCE=bigquery and GOOGLE_APPLICATION_CREDENTIALS for cloud.
"""
import os
from pathlib import Path
from typing import Tuple

import pandas as pd


def _is_bigquery_enabled() -> bool:
    return os.getenv("DATA_SOURCE", "").lower() == "bigquery"


def load_retention_data(data_dir: Path) -> pd.DataFrame:
    """Load retention data from CSV or BigQuery."""
    if _is_bigquery_enabled():
        return _load_bigquery_retention()
    path = data_dir / "retention_data.csv"
    if not path.exists():
        raise FileNotFoundError(f"Retention data not found at {path}. Run python src/train.py first.")
    df = pd.read_csv(path)
    df["exit_date"] = pd.to_datetime(df["exit_date"], errors="coerce")
    return df


def load_lead_data(data_dir: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load GA4, CRM, SIS from CSV or BigQuery."""
    if _is_bigquery_enabled():
        return _load_bigquery_lead()
    for f in ["ga4_data.csv", "crm_data.csv", "sis_data.csv"]:
        if not (data_dir / f).exists():
            raise FileNotFoundError(f"Lead data ({f}) not found. Run python src/train.py first.")
    ga4 = pd.read_csv(data_dir / "ga4_data.csv")
    crm = pd.read_csv(data_dir / "crm_data.csv")
    sis = pd.read_csv(data_dir / "sis_data.csv")
    return ga4, crm, sis


def _load_bigquery_retention() -> pd.DataFrame:
    try:
        from google.cloud import bigquery
    except ImportError as e:
        raise ImportError("Install google-cloud-bigquery: pip install google-cloud-bigquery") from e

    project = os.getenv("GCP_PROJECT", "your-project-id")
    dataset = os.getenv("BQ_DATASET", "student_prediction")
    table = os.getenv("BQ_RETENTION_TABLE", "retention")
    full_table = f"{project}.{dataset}.{table}"

    client = bigquery.Client()
    df = client.query(f"SELECT * FROM `{full_table}`").to_dataframe()
    df["exit_date"] = pd.to_datetime(df.get("exit_date"), errors="coerce")
    return df


def _load_bigquery_lead() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    try:
        from google.cloud import bigquery
    except ImportError as e:
        raise ImportError("Install google-cloud-bigquery: pip install google-cloud-bigquery") from e

    project = os.getenv("GCP_PROJECT", "your-project-id")
    dataset = os.getenv("BQ_DATASET", "student_prediction")

    def _q(table: str) -> pd.DataFrame:
        full = f"{project}.{dataset}.{table}"
        return bigquery.Client().query(f"SELECT * FROM `{full}`").to_dataframe()

    ga4 = _q(os.getenv("BQ_GA4_TABLE", "ga4"))
    crm = _q(os.getenv("BQ_CRM_TABLE", "crm"))
    sis = _q(os.getenv("BQ_SIS_TABLE", "sis"))
    return ga4, crm, sis


def save_to_bigquery_if_enabled(df: pd.DataFrame, table_name: str) -> None:
    """Optionally write DataFrame to BigQuery (e.g. after training)."""
    if not _is_bigquery_enabled():
        return
    try:
        from google.cloud import bigquery
    except ImportError:
        return

    project = os.getenv("GCP_PROJECT")
    dataset = os.getenv("BQ_DATASET", "student_prediction")
    if not project:
        return

    client = bigquery.Client()
    table_id = f"{project}.{dataset}.{table_name}"
    job = client.load_table_from_dataframe(df, table_id)
    job.result()
