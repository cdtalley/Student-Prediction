"""
Interactive Streamlit dashboard for student retention and lead scoring models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import joblib
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.feature_engineering import RetentionFeatureEngineer, LeadScoringFeatureEngineer
from src.models import RetentionModel, LeadScoringModel
from src.data_generation import load_config

# Page config
st.set_page_config(
    page_title="Student Prediction Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load all datasets."""
    data_dir = Path('data')
    retention_df = pd.read_csv(data_dir / 'retention_data.csv')
    ga4_df = pd.read_csv(data_dir / 'ga4_data.csv')
    crm_df = pd.read_csv(data_dir / 'crm_data.csv')
    sis_df = pd.read_csv(data_dir / 'sis_data.csv')
    return retention_df, ga4_df, crm_df, sis_df


@st.cache_resource
def load_models():
    """Load trained models."""
    models_dir = Path('models')
    
    early_model = RetentionModel.load(models_dir / 'retention_early_model.pkl')
    mid_model = RetentionModel.load(models_dir / 'retention_mid_model.pkl')
    lead_model = LeadScoringModel.load(models_dir / 'lead_scoring_model.pkl')
    
    return early_model, mid_model, lead_model


def plot_roc_curve(y_true, y_pred_proba, title="ROC Curve"):
    """Plot ROC curve."""
    from sklearn.metrics import roc_curve, auc
    
    fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
    roc_auc = auc(fpr, tpr)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines',
        name=f'ROC (AUC = {roc_auc:.3f})',
        line=dict(width=3)
    ))
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Random',
        line=dict(dash='dash', color='gray')
    ))
    fig.update_layout(
        title=title,
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        height=400,
        showlegend=True
    )
    return fig


def plot_feature_importance(importance_dict, title="Feature Importance", top_n=15):
    """Plot feature importance."""
    sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]
    features, importances = zip(*sorted_features)
    
    fig = go.Figure(go.Bar(
        x=importances,
        y=features,
        orientation='h',
        marker=dict(color=importances, colorscale='Viridis')
    ))
    fig.update_layout(
        title=title,
        xaxis_title='Importance',
        height=500,
        yaxis={'categoryorder': 'total ascending'}
    )
    return fig


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Prediction Analytics Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Project",
        ["Student Retention", "Lead Scoring", "Model Performance", "Data Overview"]
    )
    
    # Load data and models
    try:
        retention_df, ga4_df, crm_df, sis_df = load_data()
        early_model, mid_model, lead_model = load_models()
    except Exception as e:
        st.error(f"Error loading data/models: {e}")
        st.info("Please run `python src/train.py` first to generate data and train models.")
        return
    
    if page == "Student Retention":
        st.header("📊 Student Retention Prediction")
        
        tab1, tab2, tab3 = st.tabs(["Early Semester Model", "Mid-Semester Model", "Individual Prediction"])
        
        with tab1:
            st.subheader("Early Semester Risk Assessment")
            st.write("Predicts student dropout risk using data available at the beginning of the semester.")
            
            # Load early model results (would need to be saved)
            # For now, show data insights
            early_features = RetentionFeatureEngineer().create_early_semester_features(retention_df)
            early_feature_cols = RetentionFeatureEngineer().get_feature_columns('early')
            X_early = early_features[early_feature_cols]
            y_early = early_features['withdrawn']
            
            # Predictions
            early_pred = early_model.predict(X_early)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", f"{len(early_features):,}")
            with col2:
                st.metric("At Risk (Early)", f"{(early_pred > 0.5).sum():,}", 
                         f"{(early_pred > 0.5).mean()*100:.1f}%")
            with col3:
                st.metric("High Risk (>70%)", f"{(early_pred > 0.7).sum():,}")
            with col4:
                st.metric("Actual Withdrawal Rate", f"{y_early.mean()*100:.1f}%")
            
            # Risk distribution
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=early_pred,
                nbinsx=30,
                name='Risk Score Distribution',
                marker_color='steelblue'
            ))
            fig.update_layout(
                title="Early Semester Risk Score Distribution",
                xaxis_title="Dropout Probability",
                yaxis_title="Number of Students",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance
            if hasattr(early_model, 'model'):
                importance = dict(zip(early_model.feature_names, 
                                      early_model.model.feature_importances_))
                fig = plot_feature_importance(importance, "Top Features - Early Semester Model")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Mid-Semester Risk Assessment")
            st.write("Enhanced predictions using mid-semester performance data.")
            
            mid_features = RetentionFeatureEngineer().create_mid_semester_features(retention_df)
            mid_feature_cols = RetentionFeatureEngineer().get_feature_columns('mid')
            X_mid = mid_features[mid_feature_cols]
            y_mid = mid_features['withdrawn']
            
            mid_pred = mid_model.predict(X_mid)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", f"{len(mid_features):,}")
            with col2:
                st.metric("At Risk (Mid)", f"{(mid_pred > 0.5).sum():,}",
                         f"{(mid_pred > 0.5).mean()*100:.1f}%")
            with col3:
                st.metric("High Risk (>70%)", f"{(mid_pred > 0.7).sum():,}")
            with col4:
                st.metric("Actual Withdrawal Rate", f"{y_mid.mean()*100:.1f}%")
            
            # Comparison
            comparison_df = pd.DataFrame({
                'Early Risk': early_pred[:len(mid_pred)],
                'Mid Risk': mid_pred,
                'Withdrawn': y_mid.values
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=comparison_df['Early Risk'],
                y=comparison_df['Mid Risk'],
                mode='markers',
                marker=dict(
                    color=comparison_df['Withdrawn'],
                    colorscale='RdYlGn',
                    size=5,
                    opacity=0.6
                ),
                text=comparison_df['Withdrawn'].apply(lambda x: 'Withdrawn' if x == 1 else 'Retained'),
                name='Students'
            ))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                name='Equal Risk',
                line=dict(dash='dash', color='gray')
            ))
            fig.update_layout(
                title="Early vs Mid-Semester Risk Comparison",
                xaxis_title="Early Semester Risk Score",
                yaxis_title="Mid-Semester Risk Score",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance
            if hasattr(mid_model, 'model'):
                importance = dict(zip(mid_model.feature_names, 
                                    mid_model.model.feature_importances_))
                fig = plot_feature_importance(importance, "Top Features - Mid-Semester Model")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Individual Student Risk Prediction")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Student Demographics**")
                age = st.slider("Age", 17, 35, 20)
                gpa_hs = st.slider("High School GPA", 2.0, 4.0, 3.2, 0.1)
                sat = st.slider("SAT Score", 800, 1600, 1100, 50)
                first_gen = st.checkbox("First Generation Student")
                financial_aid = st.checkbox("Receives Financial Aid")
                part_time = st.checkbox("Part-Time Student")
            
            with col2:
                st.write("**Early Semester Performance**")
                early_attendance = st.slider("Early Attendance Rate", 0.0, 1.0, 0.85, 0.05)
                early_assignments = st.slider("Early Assignment Completion", 0.0, 1.0, 0.80, 0.05)
                
                st.write("**Mid-Semester Performance**")
                mid_gpa = st.slider("Mid-Semester GPA", 0.0, 4.0, 2.8, 0.1)
                mid_attendance = st.slider("Mid-Semester Attendance", 0.0, 1.0, 0.75, 0.05)
                tutoring = st.number_input("Tutoring Visits", 0, 20, 0)
                advisor = st.number_input("Advisor Meetings", 0, 10, 0)
            
            if st.button("Calculate Risk Score"):
                # Create feature vector
                fe = RetentionFeatureEngineer()
                
                # Early features
                risk_score = (
                    (gpa_hs < 3.0) * 0.3 + (sat < 1000) * 0.2 + 
                    first_gen * 0.15 + financial_aid * 0.1 + part_time * 0.15
                )
                
                student_data = {
                    'age': age,
                    'gpa_high_school': gpa_hs,
                    'sat_score': sat,
                    'first_gen': first_gen,
                    'financial_aid': financial_aid,
                    'part_time': part_time,
                    'early_attendance': early_attendance,
                    'early_assignments': early_assignments,
                    'mid_gpa': mid_gpa,
                    'mid_attendance': mid_attendance,
                    'mid_assignments': early_assignments + (mid_gpa - gpa_hs) * 0.1,
                    'tutoring_visits': tutoring,
                    'advisor_meetings': advisor,
                    'risk_score': risk_score,
                    'semester': 1,
                    'course_load': 12 if part_time else 15,
                    'payment_on_time': 1,
                    'financial_stress': 0
                }
                
                student_df = pd.DataFrame([student_data])
                early_feat = fe.create_early_semester_features(student_df)
                mid_feat = fe.create_mid_semester_features(student_df)
                
                early_cols = fe.get_feature_columns('early')
                mid_cols = fe.get_feature_columns('mid')
                
                early_risk = early_model.predict(early_feat[early_cols])[0]
                mid_risk = mid_model.predict(mid_feat[mid_cols])[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Early Semester Risk", f"{early_risk*100:.1f}%",
                             "🟢 Low" if early_risk < 0.3 else "🟡 Medium" if early_risk < 0.7 else "🔴 High")
                with col2:
                    st.metric("Mid-Semester Risk", f"{mid_risk*100:.1f}%",
                             "🟢 Low" if mid_risk < 0.3 else "🟡 Medium" if mid_risk < 0.7 else "🔴 High")
                
                # Recommendations
                st.subheader("Recommendations")
                if early_risk > 0.5:
                    st.warning("⚠️ Early intervention recommended. Consider:")
                    st.write("- Proactive advisor outreach")
                    st.write("- Tutoring program enrollment")
                    st.write("- Financial aid counseling if applicable")
                if mid_risk > 0.7:
                    st.error("🚨 High risk detected. Immediate action required:")
                    st.write("- Intensive academic support")
                    st.write("- Regular check-ins with advisor")
                    st.write("- Consider course load reduction")
    
    elif page == "Lead Scoring":
        st.header("🎯 Lead Scoring & Enrollment Prediction")
        
        # Merge data
        fe = LeadScoringFeatureEngineer()
        merged_df = fe.merge_sources(ga4_df, crm_df, sis_df)
        features_df = fe.create_features(merged_df)
        feature_cols = fe.get_feature_columns()
        X_lead = features_df[feature_cols]
        y_lead = features_df['enrolled']
        
        lead_pred = lead_model.predict(X_lead)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Leads", f"{len(features_df):,}")
        with col2:
            st.metric("Enrollment Rate", f"{y_lead.mean()*100:.2f}%")
        with col3:
            st.metric("High Quality Leads", f"{(lead_pred > 0.5).sum():,}")
        with col4:
            st.metric("Top 20% Leads", f"{(lead_pred > np.percentile(lead_pred, 80)).sum():,}")
        
        # Score distribution
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Enrollment Score Distribution", "Score by Enrollment Status")
        )
        
        fig.add_trace(
            go.Histogram(x=lead_pred, nbinsx=30, name='All Leads', marker_color='steelblue'),
            row=1, col=1
        )
        
        enrolled_scores = lead_pred[y_lead == 1]
        not_enrolled_scores = lead_pred[y_lead == 0]
        
        fig.add_trace(
            go.Histogram(x=enrolled_scores, nbinsx=30, name='Enrolled', marker_color='green', opacity=0.7),
            row=1, col=2
        )
        fig.add_trace(
            go.Histogram(x=not_enrolled_scores, nbinsx=30, name='Not Enrolled', marker_color='red', opacity=0.7),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature importance
        if hasattr(lead_model, 'model'):
            importance = dict(zip(lead_model.feature_names, 
                                lead_model.model.feature_importances_))
            fig = plot_feature_importance(importance, "Top Features - Lead Scoring Model")
            st.plotly_chart(fig, use_container_width=True)
        
        # Data coverage analysis
        st.subheader("Data Source Coverage")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GA4 Coverage", "100%", f"{len(ga4_df):,} leads")
        with col2:
            st.metric("CRM Coverage", f"{len(crm_df)/len(ga4_df)*100:.1f}%", f"{len(crm_df):,} leads")
        with col3:
            st.metric("SIS Coverage", f"{len(sis_df)/len(ga4_df)*100:.1f}%", f"{len(sis_df):,} leads")
    
    elif page == "Model Performance":
        st.header("📈 Model Performance Metrics")
        
        # This would show saved metrics from training
        st.info("Run `python src/train.py` to see detailed performance metrics during training.")
        
        st.subheader("Expected Performance")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Retention Models**")
            st.write("- Early Semester AUC: ~0.75-0.80")
            st.write("- Mid-Semester AUC: ~0.82-0.87")
            st.write("- Features: 15 (early) / 25 (mid)")
        
        with col2:
            st.write("**Lead Scoring Model**")
            st.write("- Enrollment Prediction AUC: ~0.78-0.85")
            st.write("- Ensemble: XGBoost + LightGBM")
            st.write("- Features: 30+ (multi-source)")
    
    else:  # Data Overview
        st.header("📋 Data Overview")
        
        tab1, tab2 = st.tabs(["Retention Data", "Lead Scoring Data"])
        
        with tab1:
            st.subheader("Student Retention Dataset")
            st.write(f"**Shape:** {retention_df.shape}")
            st.write(f"**Students:** {retention_df['student_id'].nunique():,}")
            st.write(f"**Withdrawal Rate:** {retention_df['withdrawn'].mean()*100:.2f}%")
            st.write(f"**Missing Exit Dates:** {retention_df['exit_date'].isna().sum():,} "
                    f"({retention_df['exit_date'].isna().mean()*100:.1f}%)")
            
            st.dataframe(retention_df.head(20), use_container_width=True)
            
            # Summary stats
            st.subheader("Summary Statistics")
            st.dataframe(retention_df.describe(), use_container_width=True)
        
        with tab2:
            st.subheader("Lead Scoring Datasets")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**GA4 Data**")
                st.write(f"Records: {len(ga4_df):,}")
                st.dataframe(ga4_df.head(10))
            
            with col2:
                st.write("**CRM Data**")
                st.write(f"Records: {len(crm_df):,}")
                st.write(f"Coverage: {len(crm_df)/len(ga4_df)*100:.1f}%")
                st.dataframe(crm_df.head(10))
            
            with col3:
                st.write("**SIS Data**")
                st.write(f"Records: {len(sis_df):,}")
                st.write(f"Coverage: {len(sis_df)/len(ga4_df)*100:.1f}%")
                st.dataframe(sis_df.head(10))


if __name__ == '__main__':
    main()
