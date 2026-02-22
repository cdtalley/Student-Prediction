"""
API tests for Student Prediction backend.
Run from project root: python -m pytest tests/ -v
Requires: pip install pytest httpx (or use FastAPI TestClient which needs httpx).
"""
import pytest
from fastapi.testclient import TestClient

# Import app after path is set (conftest adds project root)
from api.main import app

client = TestClient(app)


def test_health():
    """Health endpoint returns 200 and expected payload."""
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("status") == "ok"
    assert "student-prediction" in data.get("service", "").lower()


def test_health_cors():
    """Health responds to preflight if CORS is used."""
    r = client.options("/api/health")
    # FastAPI may return 200 or 405 for OPTIONS depending on config
    assert r.status_code in (200, 405)


@pytest.mark.skipif(
    not __import__("pathlib").Path(__file__).resolve().parent.parent.joinpath("data", "retention_data.csv").exists(),
    reason="Data not generated (run python src/train.py)",
)
def test_stakeholder_structure():
    """Stakeholder dashboard returns 200 and expected top-level keys when data exists."""
    r = client.get("/api/stakeholder")
    if r.status_code == 503:
        pytest.skip("Backend returned 503 (data or models missing)")
    assert r.status_code == 200
    data = r.json()
    for key in ("retention", "lead_scoring", "model_performance"):
        assert key in data
    assert "stats" in data["retention"]
    assert "by_semester" in data["retention"]
    assert "bands" in data["retention"]
    assert "stats" in data["lead_scoring"]
    assert "traffic_sources" in data["lead_scoring"]
    assert isinstance(data["model_performance"], list)
    assert len(data["model_performance"]) >= 1


@pytest.mark.skipif(
    not __import__("pathlib").Path(__file__).resolve().parent.parent.joinpath("data", "retention_data.csv").exists(),
    reason="Data not generated",
)
def test_data_pipeline_retention():
    """Data pipeline retention returns 200 and expected structure when data exists."""
    r = client.get("/api/data-pipeline/retention")
    if r.status_code == 503:
        pytest.skip("Data or models missing")
    assert r.status_code == 200
    data = r.json()
    assert "stats" in data
    assert "distributions" in data
    assert "real_world_issues" in data
    assert "total_records" in data["stats"] or "n_students" in data["stats"]


@pytest.mark.skipif(
    not __import__("pathlib").Path(__file__).resolve().parent.parent.joinpath("data", "ga4_data.csv").exists(),
    reason="Lead data not generated",
)
def test_data_pipeline_lead():
    """Data pipeline lead returns 200 and expected structure when data exists."""
    r = client.get("/api/data-pipeline/lead-scoring")
    if r.status_code == 503:
        pytest.skip("Lead data or models missing")
    assert r.status_code == 200
    data = r.json()
    assert "stats" in data
    assert "join_coverage" in data
    assert "ga4_distributions" in data or "source_breakdown" in data


def test_stakeholder_returns_json_on_error():
    """When data is missing, API returns JSON error (503) with detail."""
    # If data exists we get 200; if not we get 503 with message
    r = client.get("/api/stakeholder")
    assert r.headers.get("content-type", "").startswith("application/json")
    if r.status_code == 503:
        body = r.json()
        assert "detail" in body
