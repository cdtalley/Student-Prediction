# Stakeholder Demo Notebook

**Run this to show the full ML pipeline and answer tough stakeholder questions.**

## How to run

From project root:

```bash
# Ensure data and models exist (or will be generated)
python src/train.py

# Launch Jupyter
jupyter notebook notebooks/stakeholder_demo.ipynb
```

Or with VS Code / Cursor: open `stakeholder_demo.ipynb` and run all cells.

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
