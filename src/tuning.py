"""
Hyperparameter tuning for retention and lead scoring models.
Uses Optuna with stratified K-fold CV and pruning for efficient search.
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE
from typing import Dict, Optional, Any
import optuna
from optuna.samplers import TPESampler

# Reduce Optuna log verbosity
optuna.logging.set_verbosity(optuna.logging.WARNING)


def _prepare_data(
    X: pd.DataFrame, y: pd.Series, use_smote: bool = True, random_state: int = 42
) -> tuple:
    """Resample with SMOTE if requested. Returns (X, y) ready for CV."""
    X = X.fillna(X.median()).replace([np.inf, -np.inf], np.nan).fillna(X.median())
    if use_smote:
        smote = SMOTE(random_state=random_state)
        X_res, y_res = smote.fit_resample(X, y)
        return pd.DataFrame(X_res, columns=X.columns), pd.Series(y_res)
    return X, y


def tune_retention_model(
    X: pd.DataFrame,
    y: pd.Series,
    n_trials: int = 80,
    cv_folds: int = 5,
    random_state: int = 42,
    timeout: Optional[float] = 600,
    show_progress: bool = True,
) -> Dict[str, Any]:
    """
    Tune XGBoost hyperparameters for retention using Optuna.
    Returns best params and study for inspection.
    """
    X_res, y_res = _prepare_data(X, y, use_smote=True, random_state=random_state)
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
            "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
            "random_state": random_state,
            "eval_metric": "auc",
        }
        model = XGBClassifier(**params)
        scores = cross_val_score(
            model, X_res, y_res, cv=skf, scoring="roc_auc", n_jobs=1
        )
        return scores.mean()

    sampler = TPESampler(n_startup_trials=20, seed=random_state)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(
        objective,
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=show_progress,
        gc_after_trial=True,
    )

    best = study.best_params
    best["random_state"] = random_state
    best["eval_metric"] = "auc"

    return {"best_params": best, "best_value": study.best_value, "study": study}


def tune_lead_scoring_model(
    X: pd.DataFrame,
    y: pd.Series,
    n_trials: int = 60,
    cv_folds: int = 5,
    random_state: int = 42,
    timeout: Optional[float] = 600,
    show_progress: bool = True,
) -> Dict[str, Any]:
    """
    Tune XGBoost + LightGBM ensemble for lead scoring.
    Optimizes both models and ensemble weights.
    """
    X_res, y_res = _prepare_data(X, y, use_smote=True, random_state=random_state)
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)

    def objective(trial: optuna.Trial) -> float:
        # XGBoost params
        xgb_params = {
            "n_estimators": trial.suggest_int("xgb_n_estimators", 100, 400),
            "max_depth": trial.suggest_int("xgb_max_depth", 3, 8),
            "learning_rate": trial.suggest_float("xgb_lr", 0.01, 0.2, log=True),
            "subsample": trial.suggest_float("xgb_subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("xgb_colsample", 0.6, 1.0),
            "min_child_weight": trial.suggest_int("xgb_min_child", 1, 8),
            "reg_alpha": trial.suggest_float("xgb_alpha", 1e-8, 5.0, log=True),
            "reg_lambda": trial.suggest_float("xgb_lambda", 1e-8, 5.0, log=True),
            "random_state": random_state,
            "eval_metric": "auc",
        }
        # LightGBM params
        lgb_params = {
            "n_estimators": trial.suggest_int("lgb_n_estimators", 100, 400),
            "max_depth": trial.suggest_int("lgb_max_depth", 3, 10),
            "learning_rate": trial.suggest_float("lgb_lr", 0.01, 0.2, log=True),
            "num_leaves": trial.suggest_int("lgb_num_leaves", 20, 150),
            "min_child_samples": trial.suggest_int("lgb_min_child", 5, 80),
            "subsample": trial.suggest_float("lgb_subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("lgb_colsample", 0.6, 1.0),
            "reg_alpha": trial.suggest_float("lgb_alpha", 1e-8, 5.0, log=True),
            "reg_lambda": trial.suggest_float("lgb_lambda", 1e-8, 5.0, log=True),
            "random_state": random_state,
            "verbose": -1,
        }
        # Ensemble weight for XGB (lgb weight = 1 - xgb_weight)
        xgb_weight = trial.suggest_float("xgb_weight", 0.3, 0.8)

        cv_scores = []
        for train_idx, val_idx in skf.split(X_res, y_res):
            X_tr, X_val = X_res.iloc[train_idx], X_res.iloc[val_idx]
            y_tr, y_val = y_res.iloc[train_idx], y_res.iloc[val_idx]

            xgb = XGBClassifier(
                n_estimators=xgb_params["n_estimators"],
                max_depth=xgb_params["max_depth"],
                learning_rate=xgb_params["learning_rate"],
                subsample=xgb_params["subsample"],
                colsample_bytree=xgb_params["colsample_bytree"],
                min_child_weight=xgb_params["min_child_weight"],
                reg_alpha=xgb_params["reg_alpha"],
                reg_lambda=xgb_params["reg_lambda"],
                random_state=random_state,
                eval_metric="auc",
            )
            lgb = LGBMClassifier(
                n_estimators=lgb_params["n_estimators"],
                max_depth=lgb_params["max_depth"],
                learning_rate=lgb_params["learning_rate"],
                num_leaves=lgb_params["num_leaves"],
                min_child_samples=lgb_params["min_child_samples"],
                subsample=lgb_params["subsample"],
                colsample_bytree=lgb_params["colsample_bytree"],
                reg_alpha=lgb_params["reg_alpha"],
                reg_lambda=lgb_params["reg_lambda"],
                random_state=random_state,
                verbose=-1,
            )

            xgb.fit(X_tr, y_tr, verbose=False)
            lgb.fit(X_tr, y_tr)

            xgb_p = xgb.predict_proba(X_val)[:, 1]
            lgb_p = lgb.predict_proba(X_val)[:, 1]
            ensemble_p = xgb_weight * xgb_p + (1 - xgb_weight) * lgb_p
            cv_scores.append(roc_auc_score(y_val, ensemble_p))

        return np.mean(cv_scores)

    sampler = TPESampler(n_startup_trials=15, seed=random_state)
    study = optuna.create_study(direction="maximize", sampler=sampler)
    study.optimize(
        objective,
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=show_progress,
        gc_after_trial=True,
    )

    # Reconstruct best params for each model
    bp = study.best_params
    best_xgb = {
        "n_estimators": bp["xgb_n_estimators"],
        "max_depth": bp["xgb_max_depth"],
        "learning_rate": bp["xgb_lr"],
        "subsample": bp["xgb_subsample"],
        "colsample_bytree": bp["xgb_colsample"],
        "min_child_weight": bp["xgb_min_child"],
        "reg_alpha": bp["xgb_alpha"],
        "reg_lambda": bp["xgb_lambda"],
        "random_state": random_state,
        "eval_metric": "auc",
    }
    best_lgb = {
        "n_estimators": bp["lgb_n_estimators"],
        "max_depth": bp["lgb_max_depth"],
        "learning_rate": bp["lgb_lr"],
        "num_leaves": bp["lgb_num_leaves"],
        "min_child_samples": bp["lgb_min_child"],
        "subsample": bp["lgb_subsample"],
        "colsample_bytree": bp["lgb_colsample"],
        "reg_alpha": bp["lgb_alpha"],
        "reg_lambda": bp["lgb_lambda"],
        "random_state": random_state,
        "verbose": -1,
    }
    ensemble_weight = bp["xgb_weight"]

    return {
        "best_xgb_params": best_xgb,
        "best_lgb_params": best_lgb,
        "ensemble_weight": ensemble_weight,
        "best_value": study.best_value,
        "study": study,
    }
