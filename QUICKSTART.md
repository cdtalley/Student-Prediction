# Quick Start Guide

## Step 1: Setup Environment

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Create Project Directories

```bash
python setup.py
```

This creates the necessary `data/`, `models/`, and `outputs/` directories.

## Step 3: Generate Data and Train Models

```bash
python src/train.py
```

This will:
- Generate synthetic datasets (10,000 students for retention, 15,000 leads for scoring)
- Train early-semester retention model
- Train mid-semester retention model  
- Train lead scoring ensemble model
- Save all models to `models/` directory

**Expected runtime**: 2-5 minutes depending on your machine

**Expected output**:
```
TRAINING STUDENT RETENTION MODELS
============================================================
Generating retention data...
Data shape: (25000, 25)
Withdrawal rate: 45.23%

------------------------------------------------------------
EARLY SEMESTER MODEL
------------------------------------------------------------
Features: 15
Training samples: 10000

Cross-validation AUC: 0.7823 (±0.0123)
Test AUC: 0.7891
Test AP: 0.6543
Model saved to models/retention_early_model.pkl

------------------------------------------------------------
MID-SEMESTER MODEL
------------------------------------------------------------
Features: 25
Training samples: 10000

Cross-validation AUC: 0.8456 (±0.0098)
Test AUC: 0.8521
Test AP: 0.7234
Model saved to models/retention_mid_model.pkl
```

## Step 4: Launch Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

## Troubleshooting

### Import Errors
If you get import errors, make sure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. You're running commands from the project root directory

### Model Not Found Errors
If dashboard says models not found:
1. Make sure you ran `python src/train.py` first
2. Check that `models/` directory contains `.pkl` files

### Data Generation Issues
If data generation fails:
1. Check that `data/` directory exists (run `python setup.py`)
2. Ensure you have write permissions in the project directory

## Next Steps

1. **Explore the Dashboard**: Navigate through different sections
2. **Try Individual Predictions**: Use the "Individual Prediction" tab to test the models
3. **Review Code**: Check out `src/` directory to understand the implementation
4. **Customize**: Edit `config.yaml` to adjust dataset sizes or model parameters

## Project Structure

```
Student Prediction/
├── src/                    # Source code
│   ├── data_generation.py  # Synthetic data generation
│   ├── feature_engineering.py  # Feature pipelines
│   ├── models.py          # ML models
│   └── train.py           # Training script
├── dashboard.py           # Streamlit dashboard
├── config.yaml            # Configuration
├── requirements.txt       # Dependencies
└── README.md              # Full documentation
```

## For Portfolio/Resume

See `RESUME_GUIDE.md` for:
- Resume bullet points
- Interview talking points
- LinkedIn post template
- Portfolio presentation tips
