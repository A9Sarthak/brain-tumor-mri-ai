import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["num_classes"] == 4
    assert "No Tumor" in data["classes"]

def test_samples_endpoint(client):
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    class_names = [item["class_name"] for item in data]
    assert "notumor" in class_names
    assert "glioma" in class_names
    assert "meningioma" in class_names
    assert "pituitary" in class_names

def test_performance_endpoint(client):
    response = client.get("/api/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["accuracy"] >= 0.70
    assert "per_class_report" in data
    assert "No Tumor" in data["per_class_report"]

def test_report_endpoint(client):
    payload = {
        "analysis_id": "test-id-123",
        "prediction": "No Tumor",
        "confidence": 0.985,
        "probabilities": {
            "No Tumor": 0.985,
            "Glioma Tumor": 0.005,
            "Meningioma Tumor": 0.005,
            "Pituitary Tumor": 0.005
        },
        "timestamp": "2026-09-12"
    }
    response = client.post("/api/report", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_id"] == "test-id-123"
    assert "NEUROSCAN AI" in data["report_text"]
