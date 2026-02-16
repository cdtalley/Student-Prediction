# Stakeholder Demo Notebook

**Run this to show the full ML pipeline and answer tough stakeholder questions.**

## How to run

1. **Install dependencies** (from project root):
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate data and models** (if not already done):
   ```bash
   python src/train.py
   ```

3. **Open the notebook** and run cells **in order**:
   - **Cell 1**: Run first — installs xgboost, lightgbm, imblearn, shap if missing. If it installs anything, restart the kernel and run again.
   - **Cell 2** (Setup): Sets project path and imports.
   - **Remaining cells**: Run all.

From terminal:
```bash
jupyter notebook notebooks/stakeholder_demo.ipynb
```

Or in VS Code / Cursor: open `stakeholder_demo.ipynb` → Select kernel (Python with project venv) → Run All.

## What it covers

1. **Data & EDA** — Retention and lead scoring data, quality issues (missing exit dates, sparse joins)
2. **Feature engineering** — Early (15) and mid-semester (24) retention features; lead scoring (29)
3. **Models** — Train or load; AUC, calibration, confusion matrix
4. **Stakeholder Q&A:**
   - Q1: How accurate? (ROC, precision-recall, calibration)
   - Q2: Why these features? (SHAP)
   - Q3: Fairness across demographics
   - Q4: Cost of FP vs FN — threshold choice
   - Q5: Concrete high-risk student example with explanation
   - Q6: ABCD bands and intervention prioritization
