"""
Automated unit tests for single-image prediction pipeline.
"""
import pytest
import pandas as pd
from pathlib import Path
from src.config import TEST_MANIFEST, CLASSES, BEST_MODEL_PATH
from src.predict import predict_single_image
from src.models import build_resnet50_model


@pytest.fixture(scope="module")
def sample_test_image():
    test_df = pd.read_csv(TEST_MANIFEST)
    return test_df.iloc[0]["filepath"]


@pytest.fixture(scope="module")
def smoke_model():
    smoke_path = Path("models/resnet50_smoke.keras")
    if smoke_path.exists():
        return smoke_path
    return build_resnet50_model()


def test_predict_single_image_output_structure(sample_test_image, smoke_model):
    """Verify return schema and values of single image prediction."""
    res = predict_single_image(sample_test_image, model_or_path=smoke_model)

    assert "predicted_class" in res
    assert "predicted_display_name" in res
    assert "confidence_percentage" in res
    assert "probabilities" in res
    assert "probabilities_formatted" in res

    assert res["predicted_class"] in CLASSES
    assert 0.0 <= res["confidence_percentage"] <= 100.0

    # Ensure all 4 classes present in probabilities
    for cls in CLASSES:
        assert cls in res["probabilities"]
        assert 0.0 <= res["probabilities"][cls] <= 1.0

    # Check probability sum == 1.0
    total_prob = sum(res["probabilities"].values())
    assert abs(total_prob - 1.0) < 1e-4
