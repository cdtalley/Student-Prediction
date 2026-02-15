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

Wait ~30 seconds for Superset to initialize. The `superset_config.py` enables SQLite as a datasource (required for the provisioning script).

### 3. Load data into SQLite

```powershell
python scripts/load_data_for_superset.py
```

### 4. Provision dashboards via API (recommended)

```powershell
python scripts/superset_provision.py
```

This creates the database, datasets, 11 charts, and an **Executive Dashboard** automatically.

### 5. Access Superset

- **URL:** http://localhost:8088
- **Login:** admin / admin
- **Dashboard:** http://localhost:8088/superset/dashboard/student-prediction-exec/

### 6. Manual setup (optional)

If the provisioning script fails, you can set up manually:

1. **Data** → **Databases** → **+ Database**  
   - Connection: `sqlite:////app/superset_data/student_prediction.db`  
   - Display name: `Student Prediction`

2. **Data** → **Datasets** → **+ Dataset** — add `retention`, `ga4`, `crm`, `sis`

3. **Charts** → **+ Chart** — build visualizations

4. **Dashboards** → **+ Dashboard** — combine charts

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
