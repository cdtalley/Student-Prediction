"""
Actionable insights: coach lists (at-risk students per school) and lead scores 1-100 with reasons.
Used by API and notebook for stakeholder-facing outputs.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd


# Retention band thresholds (probability -> band)
RETENTION_BAND_RANGES = [
    ("A", "Critical Risk", 0.7, 1.0),
    ("B", "High Risk", 0.5, 0.7),
    ("C", "Medium Risk", 0.3, 0.5),
    ("D", "Low Risk", 0.0, 0.3),
]

LEAD_BAND_RANGES = [
    ("A", "Hot Lead", 0.7, 1.0),
    ("B", "Warm Lead", 0.5, 0.7),
    ("C", "Cool Lead", 0.3, 0.5),
    ("D", "Cold Lead", 0.0, 0.3),
]


def _prob_to_band(prob: float, bands: List[Tuple[str, str, float, float]]) -> Tuple[str, str]:
    """Map probability to band letter and label."""
    p = max(0.0, min(1.0, float(prob)))
    for letter, label, lo, hi in bands:
        if lo <= p <= hi:
            return letter, label
    return bands[-1][0], bands[-1][1]


def _retention_risk_reasons(row: pd.Series) -> List[str]:
    """Build human-readable risk reasons from retention feature row."""
    reasons = []
    if row.get("gpa_warning") == 1:
        reasons.append("Mid-term GPA below 2.0")
    if row.get("attendance_warning") == 1:
        reasons.append("Low mid-term attendance (<70%)")
    if row.get("assignment_warning") == 1:
        reasons.append("Low assignment completion (<70%)")
    if row.get("financial_stress", 0) == 1:
        reasons.append("Financial stress indicator")
    if row.get("payment_issues", 0) == 1:
        reasons.append("Payment not on time")
    if row.get("composite_risk", 0) > 0.6:
        reasons.append("High composite risk score")
    if row.get("risk_score", 0) > 0.6:
        reasons.append("Pre-enrollment risk score high")
    if row.get("mid_gpa", 4) < 2.5:
        reasons.append(f"Current mid-GPA low ({row.get('mid_gpa', 0):.2f})")
    if row.get("first_gen", 0) == 1:
        reasons.append("First-generation student")
    if row.get("part_time", 0) == 1:
        reasons.append("Part-time enrollment")
    if row.get("support_utilization", 0) < 0.3 and row.get("composite_risk", 0) > 0.4:
        reasons.append("Low use of tutoring/advising despite risk")
    return reasons[:8]  # Cap for UI


def _lead_score_reasons(row: pd.Series) -> List[str]:
    """Build human-readable reasons for lead score from feature row."""
    reasons = []
    if row.get("form_submit", 0) == 1:
        reasons.append("Form submitted")
    if row.get("brochure_download", 0) == 1:
        reasons.append("Brochure downloaded")
    if row.get("video_watch", 0) == 1:
        reasons.append("Video watched")
    if row.get("high_engagement", 0) == 1:
        reasons.append("High web engagement")
    if row.get("engagement_score", 0) > 0.6:
        reasons.append("Strong engagement score")
    if row.get("low_bounce", 0) == 1:
        reasons.append("Low bounce rate")
    if row.get("page_views", 0) >= 10:
        reasons.append("High page views")
    if row.get("responsive", 0) == 1:
        reasons.append("Quick response to outreach")
    if row.get("total_marketing_touches", 0) >= 5:
        reasons.append("Multiple marketing touches")
    if row.get("has_crm_data", 0) == 1 and row.get("email_engagement", 0) > 0.2:
        reasons.append("Email engagement")
    if row.get("strong_application", 0) > 0.5:
        reasons.append("Strong application signals")
    if row.get("quick_application", 0) == 1:
        reasons.append("Fast application completion")
    if row.get("ga4_crm_alignment", 0) == 1:
        reasons.append("GA4-CRM engagement alignment")
    if row.get("has_sis_data", 0) == 1:
        reasons.append("Enrollment/SIS data present")
    return reasons[:10]  # Cap for UI


def prob_to_score_1_100(prob: float) -> int:
    """Map model probability to integer score 1-100."""
    p = max(0.0, min(1.0, float(prob)))
    return int(round(p * 99)) + 1


def build_coach_list(
    df: pd.DataFrame,
    mid_features: pd.DataFrame,
    risk_probs: np.ndarray,
    school_names: Optional[List[str]] = None,
    top_n: int = 100,
    school_id_filter: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Build per-school coach list: most at-risk students for intervention.
    Uses first-semester records only; one row per student (mid-semester features).
    """
    if "school_id" not in df.columns:
        df = df.copy()
        df["school_id"] = 0
    if school_names is None:
        n_schools = int(df["school_id"].max()) + 1
        school_names = [f"School {i}" for i in range(n_schools)]

    # mid_features has one row per student (first semester); align by index
    mid_features = mid_features.copy()
    mid_features["_risk_prob"] = risk_probs[: len(mid_features)]
    mid_features["_band"], mid_features["_band_label"] = zip(
        *mid_features["_risk_prob"].map(lambda p: _prob_to_band(p, RETENTION_BAND_RANGES))
    )
    # Get school_id from df (first semester rows, keyed by student_id)
    first_sem = df[df["semester"] == 1][["student_id", "school_id", "mid_gpa", "gpa_high_school"]].drop_duplicates("student_id")
    merged = mid_features.merge(first_sem, on="student_id", how="left")
    merged["school_id"] = merged["school_id"].fillna(0).astype(int)

    out = []
    for school_id in sorted(merged["school_id"].unique()):
        if school_id_filter is not None and school_id != school_id_filter:
            continue
        sub = merged[merged["school_id"] == school_id].nlargest(top_n, "_risk_prob")
        school_name = school_names[school_id] if school_id < len(school_names) else f"School {school_id}"
        students = []
        for _, r in sub.iterrows():
            reasons = _retention_risk_reasons(r)
            students.append({
                "student_id": int(r["student_id"]),
                "risk_prob": round(float(r["_risk_prob"]), 4),
                "band": r["_band"],
                "band_label": r["_band_label"],
                "reasons": reasons,
                "mid_gpa": round(float(r["mid_gpa"]), 2) if pd.notna(r.get("mid_gpa")) else None,
                "gpa_high_school": round(float(r["gpa_high_school"]), 2) if pd.notna(r.get("gpa_high_school")) else None,
            })
        out.append({
            "school_id": int(school_id),
            "school_name": school_name,
            "count": len(students),
            "students": students,
        })
    return out


def build_lead_scores_with_reasons(
    features_df: pd.DataFrame,
    lead_probs: np.ndarray,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    """
    Build lead list with score 1-100 and reasons.
    """
    score_1_100 = np.vectorize(prob_to_score_1_100)(lead_probs)
    features_df = features_df.copy()
    features_df["_score_1_100"] = score_1_100
    features_df["_prob"] = lead_probs
    features_df["_band"], features_df["_band_label"] = zip(
        *features_df["_prob"].map(lambda p: _prob_to_band(p, LEAD_BAND_RANGES))
    )
    # Top by score (highest first)
    top = features_df.nlargest(limit, "_score_1_100")
    rows = []
    for _, r in top.iterrows():
        reasons = _lead_score_reasons(r)
        rows.append({
            "lead_id": int(r["lead_id"]),
            "score_1_100": int(r["_score_1_100"]),
            "band": r["_band"],
            "band_label": r["_band_label"],
            "reasons": reasons,
            "enrolled": int(r.get("enrolled", 0)),
        })
    return rows
