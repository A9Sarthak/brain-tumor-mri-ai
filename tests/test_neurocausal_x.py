"""
Unit and integration tests for the NeuroCausal-X engine:
- Conformal Prediction Sets & Epistemic Uncertainty
- Quantitative Radiomics & Morphometry Profiler
- Counterfactual Digital Lesion Resection & Causal Attribution Delta
- FastAPI /api/analyze Integration
"""
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.conformal_engine import ConformalPredictionEngine
from backend.services.radiomics_engine import RadiomicsEngine
from backend.services.causal_inpainter import CausalInpainterEngine
from backend.services.model_service import ModelService

client = TestClient(app)

def test_conformal_prediction_engine():
    """Verify split conformal prediction sets, singleton status, and entropy."""
    # 1. Clear singleton case
    probs_confident = {
        "No Tumor": 0.02,
        "Glioma Tumor": 0.88,
        "Meningioma Tumor": 0.06,
        "Pituitary Tumor": 0.04
    }
    res = ConformalPredictionEngine.evaluate(probs_confident, alpha=0.05)
    assert res["is_singleton"] is True
    assert res["prediction_set_95"] == ["Glioma Tumor"]
    assert res["coverage_guarantee"] == "95.0%"
    assert 0.0 <= res["epistemic_uncertainty_score"] <= 1.0

    # 2. Ambiguous bimodal case (e.g. differential between Glioma and Meningioma)
    probs_ambiguous = {
        "No Tumor": 0.03,
        "Glioma Tumor": 0.52,
        "Meningioma Tumor": 0.41,
        "Pituitary Tumor": 0.04
    }
    res_amb = ConformalPredictionEngine.evaluate(probs_ambiguous, alpha=0.05)
    assert res_amb["is_singleton"] is False
    assert "Glioma Tumor" in res_amb["prediction_set_95"]
    assert "Meningioma Tumor" in res_amb["prediction_set_95"]
    assert res_amb["ambiguity_status"] == "Bimodal Differential"
    assert res_amb["epistemic_uncertainty_score"] > res["epistemic_uncertainty_score"]

def test_radiomics_biomarkers_healthy():
    """Verify healthy scans return zero lesion area and parenchymal symmetry."""
    orig_np = np.ones((224, 224, 3), dtype=np.uint8) * 120
    heatmap = np.zeros((224, 224), dtype=np.float32)

    radiomics = RadiomicsEngine.extract_biomarkers(
        orig_np=orig_np,
        heatmap=heatmap,
        predicted_class="No Tumor",
        confidence=0.92
    )
    assert radiomics["lesion_detected"] is False
    assert radiomics["estimated_area_mm2"] == 0.0
    assert radiomics["estimated_area_pixels"] == 0

def test_radiomics_biomarkers_tumor():
    """Verify focal tumor detection yields positive area, sphericity, and contour overlay."""
    orig_np = np.ones((224, 224, 3), dtype=np.uint8) * 100
    # Simulate a circular high activation region
    heatmap = np.zeros((224, 224), dtype=np.float32)
    y, x = np.ogrid[:224, :224]
    dist_from_center = np.sqrt((x - 112) ** 2 + (y - 112) ** 2)
    heatmap[dist_from_center <= 30] = 0.95

    radiomics = RadiomicsEngine.extract_biomarkers(
        orig_np=orig_np,
        heatmap=heatmap,
        predicted_class="Glioma Tumor",
        confidence=0.86
    )
    assert radiomics["lesion_detected"] is True
    assert radiomics["estimated_area_mm2"] > 0.0
    assert radiomics["estimated_area_pixels"] > 0
    assert 0.0 < radiomics["sphericity_index"] <= 1.0
    assert radiomics["contour_overlay_base64"] is not None
    assert radiomics["bounding_box"] is not None

def test_causal_inpainter_digital_resection():
    """Verify counterfactual digital lesion resection computes Delta-P causal attribution."""
    model_service = ModelService.get_instance()
    orig_np = np.ones((224, 224, 3), dtype=np.uint8) * 128
    binary_mask = np.zeros((224, 224), dtype=np.uint8)
    binary_mask[80:140, 80:140] = 255  # simulated lesion

    original_probs = {
        "No Tumor": 0.05,
        "Glioma Tumor": 0.85,
        "Meningioma Tumor": 0.06,
        "Pituitary Tumor": 0.04
    }

    cf_res = CausalInpainterEngine.resect_and_evaluate(
        orig_np=orig_np,
        binary_mask=binary_mask,
        predicted_class="Glioma Tumor",
        original_confidence=0.85,
        original_probabilities=original_probs,
        model_service=model_service
    )

    assert "counterfactual_image_base64" in cf_res
    assert cf_res["causal_attribution_delta"] > 0.0
    assert "Causal Grounding" in cf_res["causal_verification_status"]

def test_analyze_endpoint_returns_neurocausal_payload():
    """Verify live /api/analyze includes conformal, radiomics, and counterfactual results."""
    response = client.post("/api/analyze", data={"sample_class": "glioma"})
    assert response.status_code == 200
    data = response.json()

    assert "conformal_prediction" in data and data["conformal_prediction"] is not None
    cp = data["conformal_prediction"]
    assert "prediction_set_95" in cp
    assert "coverage_guarantee" in cp
    assert cp["coverage_guarantee"] == "95.0%"

    assert "radiomics" in data and data["radiomics"] is not None
    rad = data["radiomics"]
    assert "estimated_area_mm2" in rad
    assert "sphericity_index" in rad
    assert "anatomical_locus" in rad

    assert "counterfactual" in data and data["counterfactual"] is not None
    cf = data["counterfactual"]
    assert "counterfactual_image_base64" in cf
    assert "causal_attribution_delta" in cf
    assert "causal_verification_status" in cf

