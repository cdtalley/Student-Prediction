# Stakeholder Demo Notebook

**Run this to show the full ML pipeline and answer tough stakeholder questions.**

## How to run

1. **Activate your project venv** and install dependencies (from project root):
   ```bash
   .\venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Generate data and models** (if not already done):
   ```bash
   python src/train.py
   ```

3. **Open the notebook** — **use your project venv as the kernel** (not Anaconda base):
   - In Cursor/VS Code: Kernel picker (top right) → **Select Interpreter** → choose `.\venv\Scripts\python.exe`
   - Or: `.\venv\Scripts\python.exe -m ipykernel install --user --name=student-prediction` then pick that kernel
   - Run cells in order (Cell 1 first; if it installs packages, restart kernel and run again)

From terminal (with venv activated):
```bash
jupyter notebook notebooks/stakeholder_demo.ipynb
```

**If you see `numpy.core.multiarray failed to import`:** You're using the wrong kernel (likely Anaconda). Switch to your project `venv` Python.

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
