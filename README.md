# Student Prediction Analytics Platform

A comprehensive machine learning platform for predicting student retention and lead scoring, built with production-ready code and best practices.

## 🎯 Project Overview

This project addresses two critical business problems in higher education:

1. **Student Retention Prediction**: Predicts which students are at risk of dropping out, with models for both early-semester (beginning of term) and mid-semester (midway through) predictions. This enables proactive intervention and resource allocation.

2. **Lead Scoring**: Predicts which prospective students (leads) are most likely to enroll, integrating data from multiple sources (GA4 web analytics, CRM, and SIS) despite incomplete join coverage.

## 🏗️ Architecture

```
Student Prediction/
├── api/
│   └── main.py                # FastAPI REST API (data pipeline, models, score bands)
├── src/
│   ├── data_generation.py     # Synthetic data generation with realistic patterns
│   ├── feature_engineering.py # Feature engineering pipelines
│   ├── models.py              # XGBoost, LightGBM, ensemble models
│   └── train.py               # Training script with validation
├── web/                       # Next.js 14 dashboard (primary UI)
│   ├── src/
│   │   ├── app/               # Pages and layout
│   │   ├── components/        # Stakeholder dashboard, data pipeline, model viz
│   │   └── lib/               # API helpers
│   └── package.json
├── scripts/
│   ├── superset_provision.py  # Apache Superset dashboard provisioning via API
│   └── load_data_for_superset.py # ETL for Superset SQLite
├── data/                      # Generated CSVs (created by train.py)
├── models/                    # Trained .pkl files (created by train.py)
├── config.yaml                # Configuration
├── run.ps1                    # One-click start (Windows)
└── requirements.txt
```

## 🚀 Quick Start

### Installation

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### Generate Data and Train Models

```bash
# From project root, with PYTHONPATH set
# Windows PowerShell:
$env:PYTHONPATH = (Get-Location).Path
python src/train.py

# Or run.ps1 will auto-train if data is missing
.\run.ps1
```

This will:
- Generate synthetic datasets for retention and lead scoring
- Train early-semester retention model (15 features)
- Train mid-semester retention model (24 features)
- Train lead scoring ensemble model (XGB+LGB, 29 features)
- Save models to `models/` directory

### Launch Full Stack

```bash
# Terminal 1: FastAPI backend
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Next.js dashboard
cd web && npm install && npm run dev
```

Open **http://localhost:3000** for the stakeholder dashboard. For Apache Superset BI dashboards, see Docker setup below.

## 📊 Features

### Student Retention Models

**Early Semester Model**
- Uses data available at the beginning of the semester
- 15 features including demographics, academic preparation, and early engagement
- Enables proactive intervention before problems escalate

**Mid-Semester Model**
- Enhanced predictions using mid-semester performance data
- 24 features including GPA trends, engagement changes, and support utilization
- More accurate predictions with additional context

**Key Features:**
- Handles missing exit dates (realistic data quality issue)
- Addresses class imbalance with SMOTE
- Cross-validation for robust performance estimates
- SHAP values for model interpretability

### Lead Scoring Model

**Multi-Source Integration**
- GA4 web analytics (100% coverage)
- CRM marketing data (70% coverage - realistic join issue)
- SIS academic data (15% coverage - only enrolled students)

**Ensemble Approach**
- XGBoost + LightGBM weighted ensemble
- Handles missing data from incomplete joins
- Feature engineering across all sources

**Key Features:**
- Engagement scoring from web behavior
- Marketing touchpoint analysis
- Academic quality indicators
- Cross-source feature alignment

## 📈 Model Performance

### Retention Models
- **Early Semester**: AUC ~0.75-0.80
- **Mid-Semester**: AUC ~0.82-0.87 (improved with additional data)

### Lead Scoring
- **Enrollment Prediction**: AUC ~0.78-0.85
- Handles class imbalance (15% enrollment rate)

## 🖥️ Next.js Web Interface

A sleek, dark-themed Next.js dashboard with comprehensive data pipeline visualizations:

```bash
# Terminal 1: Start FastAPI backend
cd "Student Prediction"
$env:PYTHONPATH = (Get-Location).Path
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start Next.js frontend
cd web
npm install
npm run dev
```

Open **http://localhost:3000** for the web interface.

### Web Dashboard Sections

1. **Retention Data Pipeline** — Stats, missing data rates, feature distributions, correlation matrix
2. **Lead Scoring Data Pipeline** — Join coverage (GA4→CRM→SIS), traffic sources, distributions
3. **Retention Feature Engineering** — Pipeline steps, transformations, early vs mid features
4. **Lead Feature Engineering** — Merge strategy, missing data handling
5. **Retention Models** — Early/mid AUC, feature importance, **A/B/C/D risk bands with interventions**
6. **Lead Scoring Model** — AUC, top features, **A/B/C/D lead bands with interventions**

### Score Bands & Interventions

Both retention and lead scoring use ABCD bands with specific actions:
- **Retention**: A=Critical → phone+meeting, B=High → phone+advisor, C=Medium → email, D=Low → monitor
- **Leads**: A=Hot → priority call, B=Warm → phone+email, C=Cool → nurture, D=Cold → low touch

## 📊 Apache Superset (BI Dashboards)

Optional Docker-based Superset for executive dashboards:

```bash
docker-compose -f docker-compose.superset.yml up -d
python scripts/superset_provision.py   # loads data + provisions (deletes old datasets)
```

Login: `admin` / `admin` → **Executive Dashboard**

## ☁️ Cloud (Optional)

- **BigQuery**: Set `DATA_SOURCE=bigquery` and `GCP_PROJECT` to load from BigQuery instead of CSV.
- **Cloud Run**: `gcloud run deploy` with the included Dockerfile.
- See [CLOUD.md](CLOUD.md) for BigQuery setup and Cloud Functions/Run deploy.

## 🎨 Streamlit Dashboard (Legacy)

The Streamlit dashboard (`streamlit run dashboard.py`) includes:

1. **Student Retention Section**
   - Early and mid-semester risk assessments
   - Risk score distributions
   - Feature importance visualizations
   - Individual student risk calculator
   - Actionable recommendations

2. **Lead Scoring Section**
   - Enrollment probability scores
   - Score distributions by enrollment status
   - Data source coverage analysis
   - Feature importance rankings

3. **Model Performance**
   - Cross-validation metrics
   - ROC curves
   - Classification reports

4. **Data Overview**
   - Dataset summaries
   - Missing data analysis
   - Statistical summaries

## 🔧 Configuration

Edit `config.yaml` to adjust:
- Dataset sizes
- Missing data rates
- Model parameters
- File paths

## 📝 Data Quality Considerations

This project addresses real-world data challenges:

1. **Missing Exit Dates**: 35% of withdrawn students lack exit dates
2. **Incomplete Joins**: CRM data covers only 70% of leads
3. **Sparse SIS Data**: Only enrolled students have SIS records
4. **Class Imbalance**: Low enrollment rates (15%) and withdrawal rates

All models handle these issues through:
- Missing value imputation
- Feature engineering for missing data indicators
- SMOTE for class imbalance
- Robust validation strategies

## 🛠️ Technical Stack

- **ML Frameworks**: XGBoost, LightGBM, scikit-learn
- **API**: FastAPI, REST endpoints
- **Frontend**: Next.js 14, React, TypeScript
- **BI Dashboards**: Apache Superset (Docker), API-provisioned charts
- **Visualization**: Plotly, Recharts
- **Interpretability**: SHAP values
- **Data Processing**: pandas, numpy
- **Validation**: Cross-validation, stratified splits

## 📚 Best Practices Implemented

- ✅ Proper train/validation/test splits
- ✅ Cross-validation for robust metrics
- ✅ Handling class imbalance
- ✅ Feature engineering pipelines
- ✅ Model interpretability (SHAP)
- ✅ Production-ready code structure
- ✅ Configuration management
- ✅ Comprehensive documentation
- ✅ Interactive visualization dashboard

## 🎓 Use Cases

1. **Early Intervention**: Identify at-risk students at semester start
2. **Resource Allocation**: Prioritize coaching and support services
3. **Marketing Optimization**: Focus on high-quality leads
4. **Enrollment Planning**: Forecast enrollment from lead pipeline

## 📄 License

This is a portfolio project demonstrating data science and ML engineering capabilities.

## 👤 Author

Senior Data Scientist with expertise in:
- Predictive modeling and ML
- Data engineering and ETL
- Business intelligence and analytics
- Production ML systems

---

**Note**: This project uses synthetic data to demonstrate capabilities while respecting data privacy. In production, real data would be used with appropriate security and privacy measures.
