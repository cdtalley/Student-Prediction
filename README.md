# Student Prediction Analytics Platform

A comprehensive machine learning platform for predicting student retention and lead scoring, built with production-ready code and best practices.

## 🎯 Project Overview

This project addresses two critical business problems in higher education:

1. **Student Retention Prediction**: Predicts which students are at risk of dropping out, with models for both early-semester (beginning of term) and mid-semester (midway through) predictions. This enables proactive intervention and resource allocation.

2. **Lead Scoring**: Predicts which prospective students (leads) are most likely to enroll, integrating data from multiple sources (GA4 web analytics, CRM, and SIS) despite incomplete join coverage.

## 🏗️ Architecture

```
Student Prediction/
├── src/
│   ├── data_generation.py      # Synthetic data generation with realistic patterns
│   ├── feature_engineering.py  # Feature engineering pipelines
│   ├── models.py              # XGBoost, LightGBM, and ensemble models
│   └── train.py               # Training scripts with validation
├── dashboard.py               # Interactive Streamlit dashboard
├── config.yaml                # Configuration parameters
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Generate Data and Train Models

```bash
# Generate synthetic data and train all models
python src/train.py
```

This will:
- Generate synthetic datasets for retention and lead scoring
- Train early-semester retention model (15 features)
- Train mid-semester retention model (25 features)
- Train lead scoring ensemble model (30+ features)
- Save models to `models/` directory

### Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📊 Features

### Student Retention Models

**Early Semester Model**
- Uses data available at the beginning of the semester
- 15 features including demographics, academic preparation, and early engagement
- Enables proactive intervention before problems escalate

**Mid-Semester Model**
- Enhanced predictions using mid-semester performance data
- 25 features including GPA trends, engagement changes, and support utilization
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

## 🎨 Dashboard Features

The interactive Streamlit dashboard includes:

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
- **Visualization**: Plotly, Streamlit
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
