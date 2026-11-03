import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import numpy as np

from web.app import app

client = TestClient(app)

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "IBM Quantum Bell Explorer" in response.text
    assert "CHSH" in response.text

def test_api_theory():
    response = client.get("/api/theory")
    assert response.status_code == 200
    data = response.json()
    assert "chsh_bound_classical" in data
    assert data["chsh_bound_classical"] == 2.0
    assert "chsh_bound_tsirelson" in data

def test_api_results_list(tmp_path, monkeypatch):
    # Ensure results endpoint returns a list
    response = client.get("/api/results")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_run_dry_or_mock(monkeypatch):
    # Mock experiment.run_sweep to test API contract without hitting IBM Quantum API quotas in CI
    from ibm_bell import experiment
    def mock_run_sweep(cfg, backend_name=None):
        return np.zeros((cfg.angles_a.__len__(), cfg.angles_b.__len__())), "mock_backend"

    monkeypatch.setattr(experiment, "run_sweep", mock_run_sweep)

    payload = {
        "shots": 128,
        "grid_a": 3,
        "grid_b": 3,
        "backend": None,
        "mitigation": None,
        "tomography": False
    }
    response = client.post("/api/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["backend_used"] == "mock_backend"
    assert "grid" in data
    assert "saved_path" in data
