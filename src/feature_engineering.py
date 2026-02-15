"""
Feature engineering pipelines for retention and lead scoring models.
Handles missing data, feature creation, and data quality issues.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import Dict, List, Tuple


class RetentionFeatureEngineer:
    """Feature engineering for student retention prediction."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def create_early_semester_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features available at the beginning of semester."""
        features = df.copy()
        
        # Use first semester data only
        first_sem = features[features['semester'] == 1].copy()
        
        # Demographic features
        first_sem['age_normalized'] = (first_sem['age'] - first_sem['age'].mean()) / first_sem['age'].std()
        
        # Academic preparation
        first_sem['gpa_sat_interaction'] = first_sem['gpa_high_school'] * (first_sem['sat_score'] / 1600)
        first_sem['academic_prep_score'] = (
            (first_sem['gpa_high_school'] / 4.0) * 0.6 + 
            (first_sem['sat_score'] / 1600) * 0.4
        )
        
        # Risk indicators
        first_sem['risk_high'] = (first_sem['risk_score'] > 0.6).astype(int)
        first_sem['risk_medium'] = ((first_sem['risk_score'] > 0.3) & 
                                    (first_sem['risk_score'] <= 0.6)).astype(int)
        
        # Financial indicators
        first_sem['financial_risk'] = (
            (1 - first_sem['financial_aid']) * 0.5 + 
            first_sem['financial_stress'] * 0.5
        )
        
        # Early engagement (if available)
        first_sem['early_engagement_score'] = (
            first_sem['early_attendance'].fillna(0.5) * 0.6 + 
            first_sem['early_assignments'].fillna(0.5) * 0.4
        )
        
        # Course load relative to student type
        expected_load = np.where(first_sem['part_time'] == 1, 9, 15)
        first_sem['course_load_ratio'] = first_sem['course_load'] / expected_load
        
        # Missing data indicators
        first_sem['missing_early_attendance'] = first_sem['early_attendance'].isna().astype(int)
        first_sem['missing_early_assignments'] = first_sem['early_assignments'].isna().astype(int)
        
        # Fill missing values
        numeric_cols = first_sem.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['student_id', 'semester', 'enrolled', 'withdrawn']:
                first_sem[col] = first_sem[col].fillna(first_sem[col].median())
        
        return first_sem
    
    def create_mid_semester_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features available at mid-semester."""
        features = df.copy()
        
        # Use first semester mid-semester data
        first_sem = features[features['semester'] == 1].copy()
        
        # All early features
        first_sem = self.create_early_semester_features(first_sem)
        
        # Mid-semester academic performance
        first_sem['mid_gpa_normalized'] = (first_sem['mid_gpa'] - first_sem['mid_gpa'].mean()) / first_sem['mid_gpa'].std()
        first_sem['gpa_trend'] = first_sem['mid_gpa'] - first_sem['gpa_high_school']
        
        # Mid-semester engagement
        first_sem['mid_engagement_score'] = (
            first_sem['mid_attendance'] * 0.6 + 
            first_sem['mid_assignments'] * 0.4
        )
        
        # Engagement trend
        first_sem['engagement_trend'] = (
            first_sem['mid_engagement_score'] - 
            first_sem['early_engagement_score']
        )
        
        # Support services utilization
        first_sem['support_utilization'] = (
            (first_sem['tutoring_visits'] > 0).astype(int) * 0.6 + 
            (first_sem['advisor_meetings'] > 0).astype(int) * 0.4
        )
        first_sem['total_support_contacts'] = first_sem['tutoring_visits'] + first_sem['advisor_meetings']
        
        # Warning indicators
        first_sem['gpa_warning'] = (first_sem['mid_gpa'] < 2.0).astype(int)
        first_sem['attendance_warning'] = (first_sem['mid_attendance'] < 0.7).astype(int)
        first_sem['assignment_warning'] = (first_sem['mid_assignments'] < 0.7).astype(int)
        
        # Financial status
        first_sem['payment_issues'] = (1 - first_sem['payment_on_time']).astype(int)
        
        # Composite risk score
        first_sem['composite_risk'] = (
            first_sem['risk_score'] * 0.3 +
            (1 - first_sem['mid_gpa'] / 4.0) * 0.3 +
            (1 - first_sem['mid_engagement_score']) * 0.2 +
            first_sem['payment_issues'] * 0.1 +
            first_sem['financial_stress'] * 0.1
        )
        
        # Fill missing values
        numeric_cols = first_sem.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['student_id', 'semester', 'enrolled', 'withdrawn']:
                first_sem[col] = first_sem[col].fillna(first_sem[col].median())
        
        return first_sem
    
    def get_feature_columns(self, feature_set: str = 'mid') -> List[str]:
        """Get list of feature column names."""
        if feature_set == 'early':
            return [
                'age_normalized', 'gpa_high_school', 'sat_score', 'gpa_sat_interaction',
                'academic_prep_score', 'risk_high', 'risk_medium', 'financial_risk',
                'early_engagement_score', 'course_load_ratio', 'first_gen',
                'financial_aid', 'part_time', 'missing_early_attendance', 'missing_early_assignments'
            ]
        else:  # mid
            return [
                'age_normalized', 'gpa_high_school', 'sat_score', 'gpa_sat_interaction',
                'academic_prep_score', 'risk_high', 'risk_medium', 'financial_risk',
                'early_engagement_score', 'course_load_ratio', 'first_gen',
                'financial_aid', 'part_time', 'mid_gpa_normalized', 'gpa_trend',
                'mid_engagement_score', 'engagement_trend', 'support_utilization',
                'total_support_contacts', 'gpa_warning', 'attendance_warning',
                'assignment_warning', 'payment_issues', 'composite_risk'
            ]


class LeadScoringFeatureEngineer:
    """Feature engineering for lead scoring with multi-source data."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def merge_sources(self, ga4_df: pd.DataFrame, crm_df: pd.DataFrame, 
                     sis_df: pd.DataFrame) -> pd.DataFrame:
        """Merge GA4, CRM, and SIS data with proper handling of missing joins."""
        # Start with GA4 (most complete)
        merged = ga4_df.copy()
        
        # Left join CRM (70% coverage)
        merged = merged.merge(crm_df, on='lead_id', how='left')
        
        # Left join SIS (only enrolled students)
        merged = merged.merge(sis_df, on='lead_id', how='left')
        
        # Enrollment target (1 if in SIS, 0 otherwise)
        merged['enrolled'] = merged['enrolled'].fillna(0).astype(int)
        
        return merged
    
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive features from merged data."""
        features = df.copy()
        
        # GA4 features
        features['engagement_score'] = features['engagement_score']
        features['high_engagement'] = (features['engagement_score'] > features['engagement_score'].quantile(0.75)).astype(int)
        features['low_bounce'] = (features['bounce_rate'] < 0.5).astype(int)
        
        # Source encoding
        source_le = LabelEncoder()
        features['source_encoded'] = source_le.fit_transform(features['source'].fillna('unknown'))
        self.label_encoders['source'] = source_le
        
        # CRM features (with missing data handling)
        features['has_crm_data'] = features['age'].notna().astype(int)
        
        # Fill CRM missing values with median/mode
        features['age'] = features['age'].fillna(features['age'].median())
        features['lead_score'] = features['lead_score'].fillna(features['lead_score'].median())
        features['email_opens'] = features['email_opens'].fillna(0)
        features['email_clicks'] = features['email_clicks'].fillna(0)
        features['phone_contacts'] = features['phone_contacts'].fillna(0)
        features['response_time_hours'] = features['response_time_hours'].fillna(features['response_time_hours'].median())
        features['program_interest'] = features['program_interest'].fillna('Unknown')
        
        # CRM engagement metrics
        features['email_engagement'] = features['email_clicks'] / (features['email_opens'] + 1)
        features['total_marketing_touches'] = features['email_opens'] + features['phone_contacts']
        features['responsive'] = (features['response_time_hours'] < 24).astype(int)
        
        # SIS features (only for enrolled students)
        features['has_sis_data'] = features['gpa'].notna().astype(int)
        
        # Fill SIS missing values
        features['gpa'] = features['gpa'].fillna(features['gpa'].median())
        features['test_score'] = features['test_score'].fillna(features['test_score'].median())
        features['application_complete_days'] = features['application_complete_days'].fillna(
            features['application_complete_days'].median()
        )
        features['recommendation_letters'] = features['recommendation_letters'].fillna(0)
        features['financial_aid_applied'] = features['financial_aid_applied'].fillna(0)
        features['scholarship_eligible'] = features['scholarship_eligible'].fillna(0)
        
        # Academic quality indicators
        features['high_gpa'] = (features['gpa'] > 3.5).astype(int)
        features['high_test_score'] = (features['test_score'] > 1300).astype(int)
        features['strong_application'] = (
            (features['gpa'] > 3.3).astype(int) * 0.4 +
            (features['test_score'] > 1200).astype(int) * 0.3 +
            (features['recommendation_letters'] >= 2).astype(int) * 0.3
        )
        
        # Cross-source features
        features['ga4_crm_alignment'] = (
            (features['engagement_score'] > 0.5) & (features['lead_score'] > 0.5)
        ).astype(int)
        
        features['quick_application'] = (features['application_complete_days'] < 14).astype(int)
        
        # Program interest encoding
        if 'program_interest' in features.columns:
            program_le = LabelEncoder()
            features['program_interest_encoded'] = program_le.fit_transform(
                features['program_interest'].fillna('Unknown')
            )
            self.label_encoders['program_interest'] = program_le
        
        return features
    
    def get_feature_columns(self) -> List[str]:
        """Get list of feature column names."""
        return [
            'page_views', 'session_duration', 'bounce_rate', 'engagement_score',
            'high_engagement', 'low_bounce', 'source_encoded', 'form_submit',
            'brochure_download', 'video_watch', 'has_crm_data', 'age', 'lead_score',
            'email_opens', 'email_clicks', 'phone_contacts', 'email_engagement',
            'total_marketing_touches', 'responsive', 'has_sis_data', 'gpa',
            'test_score', 'high_gpa', 'high_test_score', 'strong_application',
            'application_complete_days', 'quick_application', 'recommendation_letters',
            'financial_aid_applied', 'scholarship_eligible', 'ga4_crm_alignment'
        ]
