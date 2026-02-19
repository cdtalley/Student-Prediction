"""
Synthetic data generation for student retention and lead scoring projects.
Creates realistic datasets that mirror real-world data quality issues.
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple
import yaml


class RetentionDataGenerator:
    """Generate synthetic student retention data with realistic patterns."""
    
    def __init__(self, config: Dict):
        self.config = config
        data_config = config.get('data', config)
        retention_config = data_config.get('retention', config)
        self.n_students = retention_config.get('n_students', 10000)
        self.n_semesters = retention_config.get('n_semesters', 4)
        self.missing_exit_rate = retention_config.get('missing_exit_rate', 0.35)
        self.school_names = retention_config.get('school_names', [
            "College of Arts & Sciences", "School of Engineering", "School of Business",
            "School of Health", "School of Education", "College of Liberal Arts"
        ])
        self.n_schools = retention_config.get('n_schools', len(self.school_names))
        self.n_schools = min(self.n_schools, len(self.school_names))
        self.rng = np.random.RandomState(42)
        
    def generate(self) -> pd.DataFrame:
        """Generate complete retention dataset."""
        data = []
        # Assign each student to a school (weighted so larger schools have more students)
        school_weights = self.rng.dirichlet(np.ones(self.n_schools) * 2)
        student_schools = self.rng.choice(
            self.n_schools, size=self.n_students, p=school_weights, replace=True
        )

        for student_id in range(self.n_students):
            school_id = int(student_schools[student_id])
            # Student demographics
            age = self.rng.normal(20, 3)
            age = max(17, min(35, age))
            
            gpa_high_school = self.rng.normal(3.2, 0.6)
            gpa_high_school = max(2.0, min(4.0, gpa_high_school))
            
            sat_score = self.rng.normal(1100, 200)
            sat_score = max(800, min(1600, sat_score))
            
            first_gen = self.rng.binomial(1, 0.35)
            financial_aid = self.rng.binomial(1, 0.45)
            part_time = self.rng.binomial(1, 0.25)
            
            # Risk factors
            risk_score = (
                (gpa_high_school < 3.0) * 0.3 +
                (sat_score < 1000) * 0.2 +
                first_gen * 0.15 +
                financial_aid * 0.1 +
                part_time * 0.15 +
                self.rng.random() * 0.1
            )
            
            # Generate semester-by-semester data
            enrolled = True
            semester_count = 0
            
            for sem in range(1, self.n_semesters + 1):
                if not enrolled:
                    break
                    
                semester_count += 1
                
                # Early semester features (available at start)
                if sem == 1:
                    early_attendance = self.rng.beta(5, 2) if risk_score < 0.5 else self.rng.beta(2, 5)
                    early_assignments = self.rng.beta(6, 2) if risk_score < 0.5 else self.rng.beta(2, 6)
                    early_engagement = (early_attendance + early_assignments) / 2
                    
                # Mid-semester features (available at mid-point)
                mid_gpa = gpa_high_school + self.rng.normal(0, 0.3)
                mid_gpa = max(0.0, min(4.0, mid_gpa))
                
                mid_attendance = early_attendance + self.rng.normal(0, 0.1) if sem == 1 else self.rng.beta(5, 2)
                mid_attendance = max(0, min(1, mid_attendance))
                
                mid_assignments = early_assignments + self.rng.normal(0, 0.1) if sem == 1 else self.rng.beta(6, 2)
                mid_assignments = max(0, min(1, mid_assignments))
                
                mid_engagement = (mid_attendance + mid_assignments) / 2
                
                # Interaction with support services
                tutoring_visits = self.rng.poisson(risk_score * 5)
                advisor_meetings = self.rng.poisson(risk_score * 3)
                
                # Financial indicators
                payment_on_time = self.rng.binomial(1, 0.9 - risk_score * 0.3)
                financial_stress = self.rng.binomial(1, risk_score * 0.6)
                
                # Academic performance
                course_load = self.rng.choice([12, 15, 18], p=[0.2, 0.6, 0.2])
                if part_time:
                    course_load = self.rng.choice([6, 9, 12], p=[0.3, 0.5, 0.2])
                
                # Dropout probability increases with risk and semester
                dropout_prob = min(0.95, risk_score + (sem - 1) * 0.1 + (mid_gpa < 2.0) * 0.3)
                
                if self.rng.random() < dropout_prob:
                    enrolled = False
                    exit_date = pd.Timestamp('2023-01-01') + pd.Timedelta(days=120 * (sem - 1) + self.rng.randint(30, 90))
                    
                    # Missing exit dates (realistic data quality issue)
                    if self.rng.random() < self.missing_exit_rate:
                        exit_date = pd.NaT
                else:
                    exit_date = pd.NaT
                
                # Create record
                record = {
                    'student_id': student_id,
                    'school_id': school_id,
                    'semester': sem,
                    'age': age,
                    'gpa_high_school': gpa_high_school,
                    'sat_score': sat_score,
                    'first_gen': first_gen,
                    'financial_aid': financial_aid,
                    'part_time': part_time,
                    'early_attendance': early_attendance if sem == 1 else np.nan,
                    'early_assignments': early_assignments if sem == 1 else np.nan,
                    'early_engagement': early_engagement if sem == 1 else np.nan,
                    'mid_gpa': mid_gpa,
                    'mid_attendance': mid_attendance,
                    'mid_assignments': mid_assignments,
                    'mid_engagement': mid_engagement,
                    'tutoring_visits': tutoring_visits,
                    'advisor_meetings': advisor_meetings,
                    'payment_on_time': payment_on_time,
                    'financial_stress': financial_stress,
                    'course_load': course_load,
                    'enrolled': 1 if enrolled else 0,
                    'withdrawn': 0 if enrolled else 1,
                    'exit_date': exit_date,
                    'risk_score': risk_score
                }
                
                data.append(record)
        
        df = pd.DataFrame(data)
        
        # Add some noise and missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['student_id', 'semester', 'enrolled', 'withdrawn', 'first_gen', 
                          'financial_aid', 'part_time', 'payment_on_time', 'financial_stress']:
                # Add 2% missing values
                missing_idx = self.rng.choice(df.index, size=int(len(df) * 0.02), replace=False)
                df.loc[missing_idx, col] = np.nan
        
        return df


class LeadScoringDataGenerator:
    """Generate synthetic lead scoring data from GA4, CRM, and SIS sources."""
    
    def __init__(self, config: Dict):
        self.config = config
        data_config = config.get('data', config)
        lead_config = data_config.get('lead_scoring', config)
        self.n_leads = lead_config.get('n_leads', 15000)
        self.enrollment_rate = lead_config.get('enrollment_rate', 0.15)
        self.rng = np.random.RandomState(42)
        
    def generate(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Generate GA4, CRM, and SIS datasets with realistic join coverage issues."""
        
        # GA4 data (web analytics)
        ga4_data = []
        for lead_id in range(self.n_leads):
            # Traffic source
            source = self.rng.choice(
                ['organic', 'paid_search', 'social', 'direct', 'referral', 'email'],
                p=[0.35, 0.20, 0.15, 0.10, 0.10, 0.10]
            )
            
            # Engagement metrics
            page_views = self.rng.poisson(8) if source in ['organic', 'direct'] else self.rng.poisson(5)
            session_duration = self.rng.gamma(3, 60)  # seconds
            bounce_rate = self.rng.beta(3, 7) if source == 'direct' else self.rng.beta(5, 5)
            
            # Conversion events
            form_submit = self.rng.binomial(1, 0.4)
            brochure_download = self.rng.binomial(1, 0.25)
            video_watch = self.rng.binomial(1, 0.3)
            
            ga4_data.append({
                'lead_id': lead_id,
                'source': source,
                'page_views': page_views,
                'session_duration': session_duration,
                'bounce_rate': bounce_rate,
                'form_submit': form_submit,
                'brochure_download': brochure_download,
                'video_watch': video_watch,
                'engagement_score': (page_views * 0.3 + (1 - bounce_rate) * 0.3 + 
                                    form_submit * 0.2 + brochure_download * 0.1 + video_watch * 0.1)
            })
        
        ga4_df = pd.DataFrame(ga4_data)
        
        # CRM data (marketing/sales)
        crm_data = []
        # Only 70% of leads have CRM records (join coverage issue)
        crm_lead_ids = self.rng.choice(self.n_leads, size=int(self.n_leads * 0.7), replace=False)
        
        for lead_id in crm_lead_ids:
            # Demographics
            age = self.rng.normal(22, 4)
            age = max(17, min(40, age))
            
            # Lead quality
            lead_score = self.rng.beta(4, 3)
            
            # Marketing touches
            email_opens = self.rng.poisson(lead_score * 5)
            email_clicks = self.rng.poisson(lead_score * 2)
            phone_contacts = self.rng.poisson(lead_score * 1.5)
            
            # Response time
            response_time_hours = self.rng.exponential(48)
            
            # Program interest
            program_interest = self.rng.choice(
                ['Business', 'Engineering', 'Arts', 'Sciences', 'Health'],
                p=[0.25, 0.20, 0.15, 0.20, 0.20]
            )
            
            crm_data.append({
                'lead_id': lead_id,
                'age': age,
                'lead_score': lead_score,
                'email_opens': email_opens,
                'email_clicks': email_clicks,
                'phone_contacts': phone_contacts,
                'response_time_hours': response_time_hours,
                'program_interest': program_interest
            })
        
        crm_df = pd.DataFrame(crm_data)
        
        # SIS data (student information system) - only for enrolled students
        sis_data = []
        enrolled_leads = self.rng.choice(
            self.n_leads, 
            size=int(self.n_leads * self.enrollment_rate), 
            replace=False
        )
        
        for lead_id in enrolled_leads:
            # Academic info
            gpa = self.rng.normal(3.3, 0.5)
            gpa = max(2.0, min(4.0, gpa))
            
            test_score = self.rng.normal(1150, 150)
            test_score = max(800, min(1600, test_score))
            
            # Application details
            application_complete_days = self.rng.exponential(30)
            recommendation_letters = self.rng.choice([0, 1, 2, 3], p=[0.1, 0.2, 0.5, 0.2])
            
            # Financial
            financial_aid_applied = self.rng.binomial(1, 0.6)
            scholarship_eligible = self.rng.binomial(1, 0.4)
            
            sis_data.append({
                'lead_id': lead_id,
                'gpa': gpa,
                'test_score': test_score,
                'application_complete_days': application_complete_days,
                'recommendation_letters': recommendation_letters,
                'financial_aid_applied': financial_aid_applied,
                'scholarship_eligible': scholarship_eligible,
                'enrolled': 1
            })
        
        sis_df = pd.DataFrame(sis_data)
        
        # Add missing values (realistic data quality)
        for df in [ga4_df, crm_df, sis_df]:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col != 'lead_id' and col != 'enrolled':
                    missing_idx = self.rng.choice(df.index, size=int(len(df) * 0.03), replace=False)
                    df.loc[missing_idx, col] = np.nan
        
        return ga4_df, crm_df, sis_df


def load_config(config_path: str | None = None) -> Dict:
    """Load configuration from YAML file. Uses project root if path not given."""
    if config_path is None:
        config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


if __name__ == '__main__':
    config = load_config()
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    # Generate retention data
    retention_gen = RetentionDataGenerator(config)
    retention_df = retention_gen.generate()
    retention_df.to_csv(data_dir / "retention_data.csv", index=False)
    print(f"Generated retention data: {len(retention_df)} records")
    
    # Generate lead scoring data
    lead_gen = LeadScoringDataGenerator(config)
    ga4_df, crm_df, sis_df = lead_gen.generate()
    
    ga4_df.to_csv(data_dir / "ga4_data.csv", index=False)
    crm_df.to_csv(data_dir / "crm_data.csv", index=False)
    sis_df.to_csv(data_dir / "sis_data.csv", index=False)
    
    print(f"Generated GA4 data: {len(ga4_df)} records")
    print(f"Generated CRM data: {len(crm_df)} records ({len(crm_df)/len(ga4_df)*100:.1f}% coverage)")
    print(f"Generated SIS data: {len(sis_df)} records ({len(sis_df)/len(ga4_df)*100:.1f}% coverage)")
