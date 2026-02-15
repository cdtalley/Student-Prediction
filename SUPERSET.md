# Apache Superset Dashboard

Superset provides a Looker-style BI dashboard for the student prediction data.

## Prerequisites

- Docker and Docker Compose
- Python (for loading data)

## Quick Start

### 1. Generate data (if not done)

```powershell
$env:PYTHONPATH = (Get-Location).Path
python src/train.py
```

### 2. Start Superset

```powershell
docker compose -f docker-compose.superset.yml up -d
```

Wait ~30 seconds for Superset to initialize.

### 3. Load data into SQLite

```powershell
python scripts/load_data_for_superset.py
```

### 4. Access Superset

- **URL:** http://localhost:8088
- **Login:** admin / admin

### 5. Add the database connection

1. Go to **Data** → **Databases** → **+ Database**
2. Supported databases: **SQLite**
3. Connection string: `sqlite:////app/superset_data/student_prediction.db`
4. Display name: `Student Prediction`
5. Click **Connect**

### 6. Create charts and dashboards

1. **Data** → **Datasets** → **+ Dataset** — add `retention`, `ga4`, `crm`, `sis`
2. **Charts** → **+ Chart** — build visualizations
3. **Dashboards** → **+ Dashboard** — combine charts

## Suggested charts

**Retention:**
- Withdrawal rate by semester
- Risk score distribution
- GPA vs withdrawal
- Missing exit date rate

**Lead scoring:**
- Enrollment by traffic source
- CRM vs GA4 coverage
- Lead score distribution
- Enrollment rate by program interest

## Stop Superset

```powershell
docker compose -f docker-compose.superset.yml down
```
