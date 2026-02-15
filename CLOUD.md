# Cloud Setup (Optional)

Demo uses local CSV. For production-style setup: BigQuery + Cloud Run.

## BigQuery Data Source

**Default:** Local `data/*.csv`

**BigQuery mode:** Set env vars and load from your project.

```bash
export DATA_SOURCE=bigquery
export GCP_PROJECT=your-project-id
export BQ_DATASET=student_prediction
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional table overrides (default: retention, ga4, crm, sis)
export BQ_RETENTION_TABLE=retention
export BQ_GA4_TABLE=ga4
export BQ_CRM_TABLE=crm
export BQ_SIS_TABLE=sis
```

Tables must match CSV schema. One-time: run `python src/train.py` locally to generate CSV, then load into BigQuery:

```bash
bq load --source_format=CSV student_prediction.retention data/retention_data.csv
bq load --source_format=CSV student_prediction.ga4 data/ga4_data.csv
bq load --source_format=CSV student_prediction.crm data/crm_data.csv
bq load --source_format=CSV student_prediction.sis data/sis_data.csv
```

Then train against BigQuery:

```bash
DATA_SOURCE=bigquery python src/train.py
```

## Cloud Run (API)

The Dockerfile runs `python src/train.py` at build time to generate demo data and models. No pre-build step needed for a fresh clone.

Deploy the FastAPI backend:

```bash
# Build and push (replace your-project-id)
gcloud run deploy student-prediction-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

Or use the project Dockerfile: it runs training at build time so demo works out of the box.

## Cloud Functions (Scheduled Training)

Trigger training on a schedule (e.g. weekly):

```bash
gcloud functions deploy train-models \
  --runtime python311 \
  --trigger-http \
  --entry-point train \
  --source .
```

Use a Cloud Scheduler job to call the function. For heavier training, use Cloud Run Jobs instead of Functions.

## Cost

- **BigQuery**: ~$5/TB scanned. Small datasets = cents.
- **Cloud Run**: Free tier covers light demo usage.
- **No charges** when `DATA_SOURCE` is unset (local mode).
