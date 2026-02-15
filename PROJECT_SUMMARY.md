# Student Prediction Analytics — Project Summary

**Senior Data Scientist portfolio project demonstrating end-to-end ML, API design, and BI dashboarding.**

---

## One-Line Elevator Pitch

ML platform predicting student dropout risk and enrollment probability with XGBoost/LightGBM ensembles, multi-source data integration (GA4/CRM/SIS), FastAPI REST backend, Next.js stakeholder dashboard, and Apache Superset BI dashboards—all provisioned programmatically.

---

## Implementation

| Dimension | Implementation |
|-----------|----------------|
| **ML** | Retention early/mid models (15 vs 24 features), lead scoring XGB+LGB ensemble, SMOTE, CV, SHAP, metrics persisted in artifacts |
| **Data** | Multi-source joins (70% coverage), missing-data indicators, realistic quality issues (35% missing exit dates, sparse SIS) |
| **Engineering** | FastAPI REST API, Next.js dashboard, Superset provisioning via API (datasets, ~25 charts, dashboards) |
| **Cloud (optional)** | BigQuery data source, Cloud Run deployment, config-driven (off by default for demo) |
| **Interpretability** | SHAP values, feature importance, ABCD risk bands with intervention recommendations |
| **Deployment** | Docker for Superset, modular design, config-driven, production-ready structure |

---

## Tech Stack

- **ML**: XGBoost, LightGBM, scikit-learn, imbalanced-learn (SMOTE), SHAP
- **Backend**: FastAPI, Python 3.x
- **Frontend**: Next.js 14, React, TypeScript, Recharts
- **BI**: Apache Superset (Docker), API-provisioned dashboards
- **Data**: pandas, numpy, synthetic generation with realistic patterns

---

## Key Metrics (from trained models)

- **Retention Early**: ~78–82% AUC (15 features)
- **Retention Mid**: ~82–87% AUC (24 features)
- **Lead Scoring**: ~78–85% AUC (29 features, XGB+LGB ensemble)

---

## Quick Demo Flow

1. `python src/train.py` — Generate data, train models
2. `python -m uvicorn api.main:app --port 8000` — Start API
3. `cd web && npm run dev` — Start Next.js dashboard
4. (Optional) Docker + `superset_provision.py` — Superset BI dashboards

---

## Resume Bullets (Copy-Paste Ready)

- **Built end-to-end ML platform** for student retention and lead scoring using XGBoost/LightGBM ensembles; engineered 15–29 features per model with multi-source data integration (GA4/CRM/SIS) and handling of real-world data quality issues (missing joins, class imbalance).
- **Designed FastAPI REST API** exposing model metrics, score bands, feature importance, and stakeholder aggregations; consumed by Next.js dashboard for executive KPIs and risk visualizations.
- **Provisioned Apache Superset dashboards via Python API**—automated creation of datasets, 25+ charts, and Executive Dashboard for BI stakeholders.
- **Implemented validation and interpretability** with stratified cross-validation, SHAP values, ABCD risk bands with intervention recommendations, and metrics persisted in model artifacts for real-time API exposure.

---

## Files to Highlight in Portfolio

- `api/main.py` — REST API design, stakeholder endpoint
- `src/models.py` — Retention/lead models, ensemble save/load
- `src/feature_engineering.py` — Early/mid/lead feature pipelines
- `scripts/superset_provision.py` — Superset automation
- `web/src/components/StakeholderDashboard.tsx` — Executive dashboard UI
