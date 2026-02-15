#!/usr/bin/env python3
"""
Provision Apache Superset with Student Prediction dashboards via REST API.
Creates database, datasets, charts, and a beautiful stakeholder dashboard.

Prerequisites:
  - Superset running: docker compose -f docker-compose.superset.yml up -d
  - Data loaded: python scripts/load_data_for_superset.py  (MUST run first - creates period_date)

Run: python scripts/superset_provision.py

If you see "No temporal columns found": re-run load_data_for_superset.py then this script.
Access: http://localhost:8088  (admin / admin)
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).parent.parent

BASE_URL = "http://localhost:8088"
USERNAME = "admin"
PASSWORD = "admin"
DB_CONNECTION = "sqlite:////app/superset_data/student_prediction.db"
DB_NAME = "Student Prediction"


def log(msg: str) -> None:
    print(f"  > {msg}")


def get_session_tokens() -> tuple[requests.Session, str, str]:
    """Obtain session with JWT and CSRF token. Uses session for cookie-based CSRF."""
    session = requests.Session()
    log("Logging in...")
    r = session.post(
        f"{BASE_URL}/api/v1/security/login",
        json={"username": USERNAME, "password": PASSWORD, "provider": "db"},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json()["access_token"]
    log("Getting CSRF token...")
    r2 = session.get(
        f"{BASE_URL}/api/v1/security/csrf_token/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    r2.raise_for_status()
    csrf = r2.json().get("result", "")
    log("Authenticated.")
    return session, token, csrf


def get_headers(token: str, csrf: str = "") -> dict:
    h = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if csrf:
        h["X-CSRFToken"] = csrf
    return h


def delete_existing_datasets(session: requests.Session, token: str, db_id: int, csrf: str, tables: list[str]) -> None:
    """Delete datasets for given tables. Forces clean recreate with fresh temporal config."""
    headers = get_headers(token, csrf)
    r = session.get(f"{BASE_URL}/api/v1/dataset/", headers=headers, params={"page_size": 100}, timeout=30)
    if r.status_code != 200:
        return
    for ds in r.json().get("result", []):
        ds_db = ds.get("database_id") or (ds.get("database") or {}).get("id")
        if ds_db == db_id and ds.get("table_name") in tables:
            ds_id = ds["id"]
            try:
                dr = session.delete(f"{BASE_URL}/api/v1/dataset/{ds_id}", headers=headers, timeout=30)
                if dr.status_code in (200, 204):
                    log(f"Deleted dataset '{ds.get('table_name')}' (id={ds_id})")
            except Exception:
                pass
            time.sleep(0.3)


def ensure_database(session: requests.Session, token: str, csrf: str = "") -> int:
    """Create or get the Student Prediction SQLite database. Returns database ID."""
    headers = get_headers(token, csrf)
    r = session.get(f"{BASE_URL}/api/v1/database/", headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    for db in data.get("result", []):
        if db.get("database_name") == DB_NAME:
            db_id = db["id"]
            log(f"Database '{DB_NAME}' exists (id={db_id}).")
            return db_id

    log(f"Creating database '{DB_NAME}'...")
    r = session.post(
        f"{BASE_URL}/api/v1/database/",
        headers=headers,
        json={
            "database_name": DB_NAME,
            "sqlalchemy_uri": DB_CONNECTION,
            "expose_in_sqllab": True,
            "configuration_method": "sqlalchemy_form",
        },
        timeout=30,
    )
    if r.status_code != 201:
        try:
            log(f"DB create error: {r.json()}")
        except Exception:
            pass
    if r.status_code == 201:
        db_id = r.json().get("id")
        log(f"Database created (id={db_id}).")
    else:
        r2 = session.get(f"{BASE_URL}/api/v1/database/", headers=headers, timeout=30)
        r2.raise_for_status()
        for db in r2.json().get("result", []):
            if db.get("database_name") == DB_NAME:
                return db["id"]
        r.raise_for_status()
    return db_id


def ensure_dataset(session: requests.Session, token: str, db_id: int, table_name: str, csrf: str = "", main_dttm_col: str | None = None) -> int:
    """Create or get dataset for a table. Returns dataset ID."""
    headers = get_headers(token, csrf)
    r = session.get(f"{BASE_URL}/api/v1/dataset/", headers=headers, params={"page_size": 100}, timeout=30)
    r.raise_for_status()
    data = r.json()
    for ds in data.get("result", []):
        ds_db = ds.get("database_id") or (ds.get("database") or {}).get("id")
        if ds_db == db_id and ds.get("table_name") == table_name:
            ds_id = ds["id"]
            log(f"Dataset '{table_name}' exists (id={ds_id}).")
            if main_dttm_col:
                _refresh_and_set_temporal(session, token, csrf, ds_id, main_dttm_col)
            return ds_id

    log(f"Creating dataset '{table_name}'...")
    r = session.post(
        f"{BASE_URL}/api/v1/dataset/",
        headers=headers,
        json={"database": db_id, "table_name": table_name},
        timeout=30,
    )
    r.raise_for_status()
    ds_id = r.json().get("id")
    log(f"Dataset created (id={ds_id}).")
    time.sleep(0.5)
    if main_dttm_col:
        _refresh_and_set_temporal(session, token, csrf, ds_id, main_dttm_col)
    return ds_id


def _refresh_and_set_temporal(session: requests.Session, token: str, csrf: str, dataset_id: int, col: str) -> None:
    """Refresh dataset columns (picks up period_date) and set main datetime column."""
    headers = get_headers(token, csrf)
    try:
        session.put(f"{BASE_URL}/api/v1/dataset/{dataset_id}/refresh", headers=headers, timeout=30)
        time.sleep(0.5)
    except Exception:
        pass
    r = session.get(f"{BASE_URL}/api/v1/dataset/{dataset_id}", headers=headers, timeout=30)
    if r.status_code != 200:
        log(f"Cannot fetch dataset {dataset_id}")
        return
    ds = r.json().get("result", {})
    columns = ds.get("columns") or []
    if not any(c.get("column_name") == col for c in columns):
        log(f"Column '{col}' not found. Re-run: python scripts/load_data_for_superset.py")
        return
    db_id = ds.get("database", {}).get("id") or ds.get("database_id")
    # DatasetPutSchema expects database_id; columns need only schema-allowed fields
    allowed_col_keys = {"id", "column_name", "type", "verbose_name", "description", "expression",
                        "extra", "filterable", "groupby", "is_active", "is_dttm", "python_date_format",
                        "datetime_format", "advanced_data_type", "uuid"}
    updated_cols = []
    for c in columns:
        cc = {k: v for k, v in c.items() if k in allowed_col_keys}
        cc.setdefault("filterable", True)
        cc.setdefault("groupby", True)
        if cc.get("column_name") == col:
            cc["is_dttm"] = True
        updated_cols.append(cc)
    payload = {
        "database_id": db_id,
        "table_name": ds.get("table_name"),
        "main_dttm_col": col,
        "description": ds.get("description") or "",
        "columns": updated_cols,
    }
    url = f"{BASE_URL}/api/v1/dataset/{dataset_id}"
    put_url = f"{url}?override_columns=true"
    pr = session.put(put_url, headers=headers, json=payload, timeout=30)
    if pr.status_code != 200:
        # Try minimal payload (no columns)
        minimal = {"database_id": db_id, "table_name": ds.get("table_name"), "main_dttm_col": col}
        pr = session.put(put_url, headers=headers, json=minimal, timeout=30)
    if pr.status_code != 200:
        try:
            err = pr.json().get("message", pr.text)[:200]
            log(f"Dataset update failed: {err}")
        except Exception:
            log(f"Dataset update failed: {pr.status_code}")
        return
    log(f"Set main_dttm_col={col} (temporal)")
    # Try detect_datetime_formats to help Superset recognize the column
    try:
        session.post(f"{url}/detect_datetime_formats", headers=headers, json={}, timeout=30)
    except Exception:
        pass


def get_chart_uuid(session: requests.Session, token: str, chart_id: int) -> str | None:
    """Fetch chart to get its UUID for dashboard positioning."""
    headers = get_headers(token)
    r = session.get(f"{BASE_URL}/api/v1/chart/{chart_id}", headers=headers, timeout=30)
    if r.status_code != 200:
        return None
    return r.json().get("result", {}).get("uuid")


def _chart_params(params: dict) -> dict:
    """Add datetime params so charts satisfy 'Datetime column required' when dataset has period_date."""
    out = dict(params)
    out.setdefault("time_range", "No filter")
    out.setdefault("granularity_sqla", "period_date")
    return out


def create_chart(session: requests.Session, token: str, name: str, dataset_id: int, viz_type: str, params: dict, description: str = "", dashboard_ids: list[int] | None = None, csrf: str = "") -> int:
    """Create a chart. Returns chart ID."""
    headers = get_headers(token, csrf)
    payload = {
        "slice_name": name,
        "datasource_id": dataset_id,
        "datasource_type": "table",
        "viz_type": viz_type,
        "params": json.dumps(_chart_params(params)),
        "description": description or "",
    }
    if dashboard_ids:
        payload["dashboards"] = dashboard_ids
    r = session.post(f"{BASE_URL}/api/v1/chart/", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    ch_id = r.json().get("id")
    log(f"Chart '{name}' created (id={ch_id}).")
    return ch_id


def ensure_dashboard(session: requests.Session, token: str, title: str, slug: str = "", csrf: str = "") -> int:
    """Create or get dashboard. Returns dashboard ID."""
    headers = get_headers(token, csrf)
    slug = slug or title.lower().replace(" ", "-").replace("'", "")
    r = session.get(f"{BASE_URL}/api/v1/dashboard/", headers=headers, params={"page_size": 100}, timeout=30)
    r.raise_for_status()
    for d in r.json().get("result", []):
        if d.get("slug") == slug or d.get("dashboard_title") == title:
            dash_id = d["id"]
            log(f"Dashboard '{title}' exists (id={dash_id}).")
            return dash_id
    log(f"Creating dashboard '{title}'...")
    r = session.post(
        f"{BASE_URL}/api/v1/dashboard/",
        headers=headers,
        json={"dashboard_title": title, "slug": slug, "published": True},
        timeout=30,
    )
    r.raise_for_status()
    dash_id = r.json().get("id")
    log(f"Dashboard created (id={dash_id}).")
    return dash_id


def add_charts_to_dashboard(session: requests.Session, token: str, dashboard_id: int, chart_items: list[dict], csrf: str = "") -> None:
    """Add charts to dashboard. chart_items: [{"id": int, "uuid": str, "width": int, "height": int}, ...]"""
    headers = get_headers(token, csrf)
    positions = {}
    x, y = 0, 0
    max_width = 12
    for c in chart_items:
        w = c.get("width", 6)
        h = c.get("height", 4)
        cid = c["id"]
        uuid = c.get("uuid") or str(cid)
        positions[uuid] = {
            "id": uuid,
            "type": "CHART",
            "meta": {"chartId": cid, "uuid": uuid, "width": w, "height": h},
            "x": x,
            "y": y,
            "width": w,
            "height": h,
        }
        x += w
        if x >= max_width:
            x = 0
            y += h

    r = session.get(f"{BASE_URL}/api/v1/dashboard/{dashboard_id}", headers=headers, timeout=30)
    r.raise_for_status()
    dash = r.json().get("result", {})

    payload = {
        "dashboard_title": dash.get("dashboard_title", "Student Prediction"),
        "slug": dash.get("slug", "student-prediction"),
        "position_json": json.dumps(positions),
        "published": True,
    }
    r = session.put(f"{BASE_URL}/api/v1/dashboard/{dashboard_id}", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    log("Charts added to dashboard.")


def main():
    print("\n" + "=" * 60)
    print("  Student Prediction — Superset Dashboard Provisioning")
    print("=" * 60)
    print()

    db_path = PROJECT_ROOT / "superset_data" / "student_prediction.db"
    data_dir = PROJECT_ROOT / "data"
    if not data_dir.exists() or not (data_dir / "retention_data.csv").exists():
        print("ERROR: Data not found. Run: python src/train.py")
        exit(1)

    log("Loading data into SQLite (period_date for temporal)...")
    load_script = PROJECT_ROOT / "scripts" / "load_data_for_superset.py"
    try:
        subprocess.run([sys.executable, str(load_script)], cwd=str(PROJECT_ROOT), check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR running load_data: {e.stderr.decode() if e.stderr else e}")
        exit(1)

    if not db_path.exists():
        print("ERROR: SQLite database not created.")
        exit(1)

    try:
        session, token, csrf = get_session_tokens()
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Could not connect to Superset at {BASE_URL}")
        print(f"  Ensure Superset is running: docker compose -f docker-compose.superset.yml up -d")
        print(f"  {e}")
        exit(1)

    db_id = ensure_database(session, token, csrf)
    time.sleep(1)

    # Delete existing datasets so we recreate with correct temporal config
    log("Removing existing datasets (clean recreate)...")
    delete_existing_datasets(session, token, db_id, csrf, ["retention", "ga4", "crm", "sis"])
    time.sleep(0.5)

    # Datasets
    datasets = {}
    for name in ["retention", "ga4", "crm", "sis"]:
        try:
            main_dttm = "period_date" if name in ["retention", "ga4", "crm", "sis"] else None
            datasets[name] = ensure_dataset(session, token, db_id, name, csrf, main_dttm)
        except Exception as e:
            print(f"ERROR creating dataset '{name}': {e}")
            exit(1)
        time.sleep(0.3)

    dash_id = ensure_dashboard(session, token, "Student Prediction - Executive Dashboard", "student-prediction-exec", csrf)
    time.sleep(0.5)

    # Chart definitions: (name, dataset_key, viz_type, params, desc, w, h)
    # Error-free, datetime-optional types: bar, pie, treemap, sunburst, table, big_number_total
    chart_defs = [
        # --- RETENTION ---
        ("Withdrawal by Semester", "retention", "bar", {"metrics": ["count"], "groupby": ["semester"], "row_limit": 50}, "Withdrawal count by semester", 6, 4),
        ("Retention Funnel", "retention", "pie", {"metrics": ["count"], "groupby": ["withdrawn"], "row_limit": 10}, "Withdrawn vs enrolled", 6, 4),
        ("Part-Time vs Full-Time", "retention", "pie", {"metrics": ["count"], "groupby": ["part_time"], "row_limit": 10}, "Part-time vs full-time students", 6, 4),
        ("First-Gen & Financial Aid", "retention", "bar", {"metrics": ["count"], "groupby": ["first_gen", "financial_aid"], "row_limit": 20}, "Demographic breakdown", 6, 4),
        ("Semester x Withdrawn", "retention", "bar", {"metrics": ["count"], "groupby": ["semester", "withdrawn"], "row_limit": 50}, "Records by semester and withdrawal status", 12, 4),
        ("Risk by Outcome", "retention", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "risk_score"}}], "groupby": ["withdrawn"], "row_limit": 10}, "Avg risk score: dropouts vs retained. Intervention targeting.", 6, 5),
        ("GPA by Outcome", "retention", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "mid_gpa"}}], "groupby": ["withdrawn"], "row_limit": 10}, "Avg mid-semester GPA by retention outcome.", 6, 5),
        ("Retention Cohort Treemap", "retention", "treemap", {"metrics": ["count"], "groupby": ["semester", "withdrawn"], "row_limit": 100}, "Hierarchical: Semester -> Withdrawal. Size = count.", 6, 5),
        ("First-Gen Sunburst", "retention", "sunburst", {"metrics": ["count"], "groupby": ["semester", "first_gen", "withdrawn"], "row_limit": 80}, "Cohort drill-down: Semester -> First-gen -> Outcome.", 6, 5),
        ("Retention Cross-Tab", "retention", "table", {"query_mode": "aggregate", "metrics": ["count"], "groupby": ["semester", "withdrawn", "financial_aid"], "row_limit": 100}, "Semester x Withdrawn x Financial Aid. Executive summary.", 12, 5),
        ("Total Students (KPI)", "retention", "big_number_total", {"metric": "count"}, "Total retention records", 4, 2),
        ("Withdrawal Breakdown", "retention", "bar", {"metrics": ["count"], "groupby": ["withdrawn"], "row_limit": 10}, "Enrolled (0) vs Withdrawn (1) counts", 4, 3),
        # --- LEAD SCORING ---
        ("Traffic Sources", "ga4", "pie", {"metrics": ["count"], "groupby": ["source"]}, "Lead distribution by GA4 source", 6, 4),
        ("GA4 by Source", "ga4", "bar", {"metrics": ["count"], "groupby": ["source"]}, "Lead count by traffic source", 6, 4),
        ("Enrollment by Program", "crm", "bar", {"metrics": ["count"], "groupby": ["program_interest"]}, "Enrolled by program interest", 6, 4),
        ("CRM by Program", "crm", "pie", {"metrics": ["count"], "groupby": ["program_interest"]}, "Lead distribution by program", 6, 4),
        ("Enrolled Count", "sis", "big_number_total", {"metric": "count"}, "Total enrolled in SIS", 4, 2),
        ("SIS Financial Aid", "sis", "pie", {"metrics": ["count"], "groupby": ["financial_aid_applied"]}, "Enrolled by financial aid status", 6, 4),
        ("Lead Flow Treemap", "crm", "treemap", {"metrics": ["count"], "groupby": ["program_interest"], "row_limit": 50}, "Pipeline by program. Size = lead count.", 6, 5),
        ("Engagement by Source", "ga4", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "engagement_score"}}, {"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "page_views"}}], "groupby": ["source"], "row_limit": 20}, "Avg engagement and page views by source. Source ROI.", 8, 5),
        ("Form Submit Rate by Source", "ga4", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "form_submit"}}], "groupby": ["source"]}, "Form submit rate by source. Conversion attribution.", 6, 5),
        ("Lead Score by Program", "crm", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "lead_score"}}], "groupby": ["program_interest"], "row_limit": 20}, "Avg CRM lead score by program. Quality comparison.", 8, 5),
        ("GPA by Scholarship", "sis", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "gpa"}}], "groupby": ["scholarship_eligible"]}, "Enrolled GPA by scholarship eligibility.", 6, 5),
        ("Application Velocity", "sis", "bar", {"metrics": [{"expressionType": "SIMPLE", "aggregate": "AVG", "column": {"column_name": "application_complete_days"}}], "groupby": ["recommendation_letters"], "row_limit": 10}, "Avg days to complete application by rec letters.", 6, 5),
        ("Program Pipeline", "crm", "table", {"query_mode": "aggregate", "metrics": ["count"], "groupby": ["program_interest"], "row_limit": 50}, "Program lead counts. Pipeline summary.", 8, 5),
    ]

    chart_items = []
    for name, ds_key, viz, params, desc, w, h in chart_defs:
        try:
            ch_id = create_chart(session, token, name, datasets[ds_key], viz, params, desc, dashboard_ids=[dash_id], csrf=csrf)
            time.sleep(0.3)
            uuid = get_chart_uuid(session, token, ch_id)
            chart_items.append({"id": ch_id, "uuid": uuid, "width": w, "height": h})
        except Exception as e:
            log(f"Skipped '{name}': {e}")

    if not chart_items:
        print("ERROR: No charts were created. Check Superset logs.")
        exit(1)

    try:
        add_charts_to_dashboard(session, token, dash_id, chart_items, csrf)
    except Exception as e:
        print(f"ERROR creating dashboard: {e}")
        exit(1)

    print()
    print("=" * 60)
    print("  Done!")
    print("=" * 60)
    print(f"\n  Dashboard: {BASE_URL}/dashboard/list/")
    print(f"  Or: {BASE_URL}/superset/dashboard/student-prediction-exec/\n")


if __name__ == "__main__":
    main()
