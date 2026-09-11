"""
Automated unit tests for ResNet50 transfer learning architecture,
output shapes, parameter counts, and softmax properties.
"""
import pytest
import numpy as np
import tensorflow as tf

from src.models import build_resnet50_model
from src.config import INPUT_SHAPE, NUM_CLASSES


@pytest.fixture(scope="module")
def model():
    return build_resnet50_model()


def test_model_input_output_shapes(model):
    """Verify input shape is (None, 224, 224, 3) and output is (None, 4)."""
    assert model.input_shape == (None, 224, 224, 3)
    assert model.output_shape == (None, 4)


def test_backbone_is_frozen(model):
    """Verify base ResNet50 backbone layers are non-trainable in Phase 1."""
    # The classification head (Dense, BatchNorm, Dense) should be trainable
    # Backbone conv layers should be non-trainable
    trainable_count = len(model.trainable_weights)
    non_trainable_count = len(model.non_trainable_weights)
    assert non_trainable_count > 100, f"Expected frozen backbone, got {non_trainable_count} non-trainable weights"
    assert trainable_count > 0, "Classification head must be trainable"


def test_model_forward_pass_softmax_properties(model):
    """Verify forward pass generates valid probability distribution summing to 1."""
    dummy_input = tf.random.normal((2, 224, 224, 3))
    preds = model(dummy_input, training=False).numpy()
    
    assert preds.shape == (2, 4)
    # Probabilities in [0, 1]
    assert np.all(preds >= 0.0)
    assert np.all(preds <= 1.0)
    # Sum of softmax probabilities equals 1.0 within numerical epsilon
    np.testing.assert_allclose(preds.sum(axis=1), np.ones(2), atol=1e-5)
