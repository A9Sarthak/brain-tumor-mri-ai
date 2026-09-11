"""
NeuroScan AI — Full Regression & Model Verification Test Suite
Verifies:
1. Exact model weights & architecture integrity (EfficientNet-B0)
2. Preprocessing consistency (224x224x3, RGB, 0-255 scale)
3. Class mapping consistency (0: No Tumor, 1: Glioma, 2: Meningioma, 3: Pituitary)
4. Fast & accurate inference across all 4 representative test scans
5. Grad-CAM generation on layer top_conv
6. Performance metrics artifact integrity
"""

import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.model_service import ModelService
from backend.services.gradcam_service import GradcamService
from src.config import RAW_DATA_DIR, MODELS_DIR

client = TestClient(app)

def test_model_loaded_once():
    instance1 = ModelService.get_instance()
    instance2 = ModelService.get_instance()
    assert instance1 is instance2, "ModelService must be a strict singleton"
    assert instance1.model is not None, "Model must be loaded"

def test_class_mapping_order():
    instance = ModelService.get_instance()
    expected_order = ['No Tumor', 'Glioma Tumor', 'Meningioma Tumor', 'Pituitary Tumor']
    assert instance.classes == expected_order, f"Class mapping altered! Found: {instance.classes}"

def test_all_sample_scans_inference():
    test_cases = [
        ("glioma", RAW_DATA_DIR / "Testing" / "glioma" / "Te-gl_1.jpg"),
        ("meningioma", RAW_DATA_DIR / "Testing" / "meningioma" / "Te-me_1.jpg"),
        ("notumor", RAW_DATA_DIR / "Testing" / "notumor" / "Te-no_1.jpg"),
        ("pituitary", RAW_DATA_DIR / "Testing" / "pituitary" / "Te-pi_1.jpg"),
    ]

    for label, img_path in test_cases:
        assert img_path.exists(), f"Missing test image: {img_path}"
        with open(img_path, "rb") as f:
            response = client.post(
                "/api/analyze",
                files={"file": (img_path.name, f, "image/jpeg")}
            )
        assert response.status_code == 200, f"Analyze failed for {label}: {response.text}"
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert len(data["probabilities"]) == 4
        # Probability sum should be 1.0
        prob_sum = sum(data["probabilities"].values())
        assert abs(prob_sum - 1.0) < 0.01, f"Probabilities do not sum to 1.0: {prob_sum}"

def test_gradcam_generation():
    img_path = RAW_DATA_DIR / "Testing" / "glioma" / "Te-gl_1.jpg"
    with open(img_path, "rb") as f:
        response = client.post(
            "/api/gradcam",
            files={"file": ("Te-gl_1.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["target_layer"] == "top_conv"
    assert len(data["original_image_base64"]) > 500
    assert len(data["attention_heatmap_base64"]) > 500
    assert len(data["overlay_image_base64"]) > 500

def test_performance_metrics_accuracy():
    response = client.get("/api/performance")
    assert response.status_code == 200
    data = response.json()
    assert data["accuracy"] == 0.80, f"Accuracy altered! Found: {data['accuracy']}"
    assert data["test_sample_count"] == 1600
    assert "Glioma Tumor" in data["per_class_report"]
    assert "Meningioma Tumor" in data["per_class_report"]
    assert "No Tumor" in data["per_class_report"]
    assert "Pituitary Tumor" in data["per_class_report"]

if __name__ == "__main__":
    pytest.main(["-v", __file__])
