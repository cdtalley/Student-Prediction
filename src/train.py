"""
Training script for retention and lead scoring models.
Set DATA_SOURCE=bigquery to load from BigQuery instead of local CSV.
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.data_generation import RetentionDataGenerator, LeadScoringDataGenerator, load_config
from src.feature_engineering import RetentionFeatureEngineer, LeadScoringFeatureEngineer
from src.models import RetentionModel, LeadScoringModel


def _use_bigquery() -> bool:
    return os.getenv("DATA_SOURCE", "").lower() == "bigquery"


def train_retention_models(config: dict):
    """Train early and mid-semester retention models."""
    print("=" * 60)
    print("TRAINING STUDENT RETENTION MODELS")
    print("=" * 60)
    
    # Load or generate data
    data_path = Path('data/retention_data.csv')
    if _use_bigquery():
        print("Loading retention data from BigQuery...")
        from src.data_loader import load_retention_data as _load
        retention_df = _load(Path('data'))
    elif data_path.exists():
        print("Loading existing retention data...")
        retention_df = pd.read_csv(data_path)
    else:
        print("Generating retention data...")
        gen = RetentionDataGenerator(config)
        retention_df = gen.generate()
        Path('data').mkdir(exist_ok=True)
        retention_df.to_csv(data_path, index=False)
    
    print(f"Data shape: {retention_df.shape}")
    print(f"Withdrawal rate: {retention_df['withdrawn'].mean():.2%}")
    
    # Feature engineering
    fe = RetentionFeatureEngineer()
    
    # Early semester model
    print("\n" + "-" * 60)
    print("EARLY SEMESTER MODEL")
    print("-" * 60)
    
    early_features = fe.create_early_semester_features(retention_df)
    early_feature_cols = fe.get_feature_columns('early')
    
    X_early = early_features[early_feature_cols]
    y_early = early_features['withdrawn']
    
    print(f"Features: {len(early_feature_cols)}")
    print(f"Training samples: {len(X_early)}")
    
    early_model = RetentionModel(feature_set='early')
    early_results = early_model.train(X_early, y_early)
    
    print(f"\nCross-validation AUC: {early_results['cv_auc_mean']:.4f} "
          f"(±{early_results['cv_auc_std']:.4f})")
    print(f"Test AUC: {early_results['test_auc']:.4f}")
    print(f"Test AP: {early_results['test_ap']:.4f}")
    
    # Save early model
    Path('models').mkdir(exist_ok=True)
    early_model.save('models/retention_early_model.pkl')
    print("Model saved to models/retention_early_model.pkl")
    
    # Mid-semester model
    print("\n" + "-" * 60)
    print("MID-SEMESTER MODEL")
    print("-" * 60)
    
    mid_features = fe.create_mid_semester_features(retention_df)
    mid_feature_cols = fe.get_feature_columns('mid')
    
    X_mid = mid_features[mid_feature_cols]
    y_mid = mid_features['withdrawn']
    
    print(f"Features: {len(mid_feature_cols)}")
    print(f"Training samples: {len(X_mid)}")
    
    mid_model = RetentionModel(feature_set='mid')
    mid_results = mid_model.train(X_mid, y_mid)
    
    print(f"\nCross-validation AUC: {mid_results['cv_auc_mean']:.4f} "
          f"(±{mid_results['cv_auc_std']:.4f})")
    print(f"Test AUC: {mid_results['test_auc']:.4f}")
    print(f"Test AP: {mid_results['test_ap']:.4f}")
    
    # Save mid model
    mid_model.save('models/retention_mid_model.pkl')
    print("Model saved to models/retention_mid_model.pkl")
    
    # Feature importance
    print("\n" + "-" * 60)
    print("TOP FEATURES - MID SEMESTER MODEL")
    print("-" * 60)
    top_features = sorted(mid_results['feature_importance'].items(), 
                         key=lambda x: x[1], reverse=True)[:10]
    for feat, imp in top_features:
        print(f"  {feat}: {imp:.4f}")
    
    return early_model, mid_model, early_results, mid_results


def train_lead_scoring_model(config: dict):
    """Train lead scoring model."""
    print("\n" + "=" * 60)
    print("TRAINING LEAD SCORING MODEL")
    print("=" * 60)
    
    # Load or generate data
    data_dir = Path('data')
    ga4_path = data_dir / 'ga4_data.csv'
    crm_path = data_dir / 'crm_data.csv'
    sis_path = data_dir / 'sis_data.csv'

    if _use_bigquery():
        print("Loading lead scoring data from BigQuery...")
        from src.data_loader import load_lead_data as _load
        ga4_df, crm_df, sis_df = _load(data_dir)
    elif all(p.exists() for p in [ga4_path, crm_path, sis_path]):
        print("Loading existing lead scoring data...")
        ga4_df = pd.read_csv(ga4_path)
        crm_df = pd.read_csv(crm_path)
        sis_df = pd.read_csv(sis_path)
    else:
        print("Generating lead scoring data...")
        gen = LeadScoringDataGenerator(config)
        ga4_df, crm_df, sis_df = gen.generate()
        data_dir.mkdir(exist_ok=True)
        ga4_df.to_csv(ga4_path, index=False)
        crm_df.to_csv(crm_path, index=False)
        sis_df.to_csv(sis_path, index=False)
    
    print(f"GA4 records: {len(ga4_df)}")
    print(f"CRM records: {len(crm_df)} ({len(crm_df)/len(ga4_df)*100:.1f}% coverage)")
    print(f"SIS records: {len(sis_df)} ({len(sis_df)/len(ga4_df)*100:.1f}% coverage)")
    print(f"Enrollment rate: {sis_df['enrolled'].sum()/len(ga4_df)*100:.2f}%")
    
    # Feature engineering
    fe = LeadScoringFeatureEngineer()
    merged_df = fe.merge_sources(ga4_df, crm_df, sis_df)
    features_df = fe.create_features(merged_df)
    feature_cols = fe.get_feature_columns()
    
    X = features_df[feature_cols]
    y = features_df['enrolled']
    
    print(f"\nFeatures: {len(feature_cols)}")
    print(f"Training samples: {len(X)}")
    print(f"Enrollment rate: {y.mean():.2%}")
    
    # Train model
    model = LeadScoringModel()
    results = model.train(X, y)
    
    print(f"\nCross-validation AUC: {results['cv_auc_mean']:.4f} "
          f"(±{results['cv_auc_std']:.4f})")
    print(f"Test AUC: {results['test_auc']:.4f}")
    print(f"Test AP: {results['test_ap']:.4f}")
    
    # Save model
    Path('models').mkdir(exist_ok=True)
    model.save('models/lead_scoring_model.pkl')
    print("Model saved to models/lead_scoring_model.pkl")
    
    # Feature importance
    print("\n" + "-" * 60)
    print("TOP FEATURES")
    print("-" * 60)
    top_features = sorted(results['feature_importance'].items(), 
                         key=lambda x: x[1], reverse=True)[:10]
    for feat, imp in top_features:
        print(f"  {feat}: {imp:.4f}")
    
    return model, results


if __name__ == '__main__':
    config = load_config()
    
    # Train retention models
    early_model, mid_model, early_results, mid_results = train_retention_models(config)
    
    # Train lead scoring model
    lead_model, lead_results = train_lead_scoring_model(config)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)
    print("\nAll models saved to models/ directory")
