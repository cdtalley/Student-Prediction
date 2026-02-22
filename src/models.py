"""
Supervised learning models for student retention and lead scoring.
Includes XGBoost, LightGBM, and ensemble approaches with proper validation.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, average_precision_score,
    classification_report, confusion_matrix, roc_curve
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE
import joblib
from typing import Dict, Tuple, List


class RetentionModel:
    """Student retention prediction model with early and mid-semester variants."""
    
    def __init__(self, feature_set: str = 'mid', random_state: int = 42):
        self.feature_set = feature_set
        self.random_state = random_state
        self.model = None
        self.feature_names = []
        self.scaler = None
        self.shap_explainer = None
        
    def train(
        self, X: pd.DataFrame, y: pd.Series, use_smote: bool = True, params: dict = None
    ) -> Dict:
        """Train retention model with cross-validation.
        Args:
            params: Optional tuned hyperparameters (from src.tuning.tune_retention_model).
                    If None, uses sensible defaults.
        """
        # Handle class imbalance
        if use_smote:
            smote = SMOTE(random_state=self.random_state)
            X_resampled, y_resampled = smote.fit_resample(X, y)
            X_resampled = pd.DataFrame(X_resampled, columns=X.columns)
            y_resampled = pd.Series(y_resampled)
        else:
            X_resampled, y_resampled = X, y

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_resampled, y_resampled, test_size=0.2, random_state=self.random_state, stratify=y_resampled
        )

        # Use tuned params or defaults
        default_params = dict(
            n_estimators=200, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, random_state=self.random_state, eval_metric='auc'
        )
        model_params = {**default_params, **(params or {})}
        self.model = XGBClassifier(**model_params)
        
        self.model.fit(X_train, y_train, verbose=False)
        
        self.feature_names = list(X.columns)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_resampled, y_resampled,
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state),
            scoring='roc_auc'
        )
        
        # Predictions
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        y_pred = self.model.predict(X_test)
        
        # Metrics
        auc = roc_auc_score(y_test, y_pred_proba)
        ap = average_precision_score(y_test, y_pred_proba)
        
        # SHAP explainer (lazy import to avoid numba/numpy version constraints at import time)
        import shap
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        self.test_auc = auc
        self.test_ap = ap
        results = {
            'cv_auc_mean': cv_scores.mean(),
            'cv_auc_std': cv_scores.std(),
            'test_auc': auc,
            'test_ap': ap,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': dict(zip(self.feature_names, self.model.feature_importances_)),
            'y_test': y_test.values,
            'y_pred_proba': y_pred_proba
        }
        
        return results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        X = X[self.feature_names].fillna(X[self.feature_names].median())
        return self.model.predict_proba(X)[:, 1]
    
    def get_shap_values(self, X: pd.DataFrame, max_samples: int = 100) -> Tuple:
        """Get SHAP values for model interpretation."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        if self.shap_explainer is None:
            import shap
            self.shap_explainer = shap.TreeExplainer(self.model)
        
        X_sample = X.sample(min(max_samples, len(X)), random_state=self.random_state)
        shap_values = self.shap_explainer.shap_values(X_sample)
        return shap_values, X_sample
    
    def save(self, filepath: str):
        """Save model to disk."""
        joblib.dump({
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_set': self.feature_set,
            'test_auc': getattr(self, 'test_auc', None),
            'test_ap': getattr(self, 'test_ap', None),
        }, filepath)
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from disk."""
        data = joblib.load(filepath)
        instance = cls(feature_set=data['feature_set'])
        instance.model = data['model']
        instance.feature_names = data['feature_names']
        return instance


class LeadScoringModel:
    """Lead scoring model for enrollment prediction (XGBoost + LightGBM ensemble)."""
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None  # Primary (XGB) for SHAP
        self.lgb_model = None  # Second ensemble component
        self.ensemble_weights = (0.6, 0.4)
        self.feature_names = []
        self.shap_explainer = None
        
    def train(
        self, X: pd.DataFrame, y: pd.Series, use_smote: bool = True, params: dict = None
    ) -> Dict:
        """Train lead scoring model with cross-validation.
        Args:
            params: Optional from src.tuning.tune_lead_scoring_model: dict with
                    best_xgb_params, best_lgb_params, ensemble_weight.
                    If None, uses sensible defaults.
        """
        # Fill any remaining NaNs (SMOTE requires finite values)
        X = X.fillna(X.median())
        X = X.replace([np.inf, -np.inf], np.nan).fillna(X.median())

        # Handle class imbalance (enrollment is rare)
        if use_smote:
            smote = SMOTE(random_state=self.random_state)
            X_resampled, y_resampled = smote.fit_resample(X, y)
            X_resampled = pd.DataFrame(X_resampled, columns=X.columns)
            y_resampled = pd.Series(y_resampled)
        else:
            X_resampled, y_resampled = X, y

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_resampled, y_resampled, test_size=0.2, random_state=self.random_state, stratify=y_resampled
        )

        # Use tuned params or defaults
        if params:
            xgb_params = dict(params.get("best_xgb_params", {}))
            lgb_params = dict(params.get("best_lgb_params", {}))
            self.ensemble_weights = (
                params.get("ensemble_weight", 0.6),
                1 - params.get("ensemble_weight", 0.6),
            )
        else:
            xgb_params = dict(
                n_estimators=200, max_depth=5, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=self.random_state,
                eval_metric='auc', early_stopping_rounds=20
            )
            lgb_params = dict(
                n_estimators=200, max_depth=5, learning_rate=0.05,
                subsample=0.8, colsample_bytree=0.8, random_state=self.random_state, verbose=-1
            )
            self.ensemble_weights = (0.6, 0.4)

        xgb_params.setdefault("early_stopping_rounds", 20)
        xgb_model = XGBClassifier(**xgb_params)
        lgb_model = LGBMClassifier(**lgb_params)
        
        xgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        lgb_model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
        
        # Ensemble predictions (weighted average)
        w_xgb, w_lgb = self.ensemble_weights
        xgb_proba = xgb_model.predict_proba(X_test)[:, 1]
        lgb_proba = lgb_model.predict_proba(X_test)[:, 1]
        y_pred_proba = w_xgb * xgb_proba + w_lgb * lgb_proba
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        self.model = xgb_model
        self.lgb_model = lgb_model
        self.feature_names = list(X.columns)
        
        # Cross-validation on ensemble
        def ensemble_predict(X_cv):
            xgb_p = xgb_model.predict_proba(X_cv)[:, 1]
            lgb_p = lgb_model.predict_proba(X_cv)[:, 1]
            return w_xgb * xgb_p + w_lgb * lgb_p
        
        # Manual CV for ensemble
        cv_scores = []
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=self.random_state)
        for train_idx, val_idx in skf.split(X_resampled, y_resampled):
            X_cv_train, X_cv_val = X_resampled.iloc[train_idx], X_resampled.iloc[val_idx]
            y_cv_train, y_cv_val = y_resampled.iloc[train_idx], y_resampled.iloc[val_idx]
            
            xgb_cv = XGBClassifier(**{k: v for k, v in xgb_params.items() if k != "early_stopping_rounds"})
            lgb_cv = LGBMClassifier(**lgb_params)
            xgb_cv.fit(X_cv_train, y_cv_train, verbose=False)
            lgb_cv.fit(X_cv_train, y_cv_train)
            xgb_p = xgb_cv.predict_proba(X_cv_val)[:, 1]
            lgb_p = lgb_cv.predict_proba(X_cv_val)[:, 1]
            ensemble_p = w_xgb * xgb_p + w_lgb * lgb_p
            
            cv_scores.append(roc_auc_score(y_cv_val, ensemble_p))
        
        # Metrics
        auc = roc_auc_score(y_test, y_pred_proba)
        ap = average_precision_score(y_test, y_pred_proba)
        self.test_auc = auc
        self.test_ap = ap
        
        # SHAP explainer (lazy import to avoid numba/numpy version constraints at import time)
        import shap
        self.shap_explainer = shap.TreeExplainer(self.model)
        
        # Feature importance (combined)
        feature_importance = {}
        for feat in self.feature_names:
            xgb_imp = xgb_model.feature_importances_[self.feature_names.index(feat)]
            lgb_imp = lgb_model.feature_importances_[self.feature_names.index(feat)]
            feature_importance[feat] = w_xgb * xgb_imp + w_lgb * lgb_imp
        self._feature_importance = feature_importance
        
        results = {
            'cv_auc_mean': np.mean(cv_scores),
            'cv_auc_std': np.std(cv_scores),
            'test_auc': auc,
            'test_ap': ap,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': feature_importance,
            'y_test': y_test.values,
            'y_pred_proba': y_pred_proba
        }
        
        return results
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions (ensemble if lgb_model exists)."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        X = X[self.feature_names].fillna(X[self.feature_names].median())
        xgb_p = self.model.predict_proba(X)[:, 1]
        if self.lgb_model is not None:
            lgb_p = self.lgb_model.predict_proba(X)[:, 1]
            w_xgb, w_lgb = self.ensemble_weights
            return w_xgb * xgb_p + w_lgb * lgb_p
        return xgb_p
    
    def get_shap_values(self, X: pd.DataFrame, max_samples: int = 100) -> Tuple:
        """Get SHAP values for model interpretation."""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        if self.shap_explainer is None:
            import shap
            self.shap_explainer = shap.TreeExplainer(self.model)
        
        X_sample = X.sample(min(max_samples, len(X)), random_state=self.random_state)
        shap_values = self.shap_explainer.shap_values(X_sample)
        return shap_values, X_sample
    
    def save(self, filepath: str):
        """Save model to disk (includes test metrics for API)."""
        joblib.dump({
            'model': self.model,
            'lgb_model': self.lgb_model,
            'feature_names': self.feature_names,
            'ensemble_weights': self.ensemble_weights,
            'test_auc': getattr(self, 'test_auc', None),
            'test_ap': getattr(self, 'test_ap', None),
            'feature_importance': getattr(self, '_feature_importance', None),
        }, filepath)
    
    @classmethod
    def load(cls, filepath: str):
        """Load model from disk."""
        data = joblib.load(filepath)
        instance = cls()
        instance.model = data['model']
        instance.lgb_model = data.get('lgb_model')
        instance.feature_names = data['feature_names']
        instance.ensemble_weights = data.get('ensemble_weights', (0.6, 0.4))
        return instance
