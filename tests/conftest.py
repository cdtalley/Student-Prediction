"""Pytest configuration and fixtures for Student Prediction API tests."""
import sys
from pathlib import Path

# Ensure project root is on path so "from api.main import app" works when run from repo root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
