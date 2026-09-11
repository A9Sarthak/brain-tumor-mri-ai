"""
Automated unit tests for model checkpoint saving, reloading in a clean session,
and numerical prediction consistency between instances.
"""
import pytest
import tempfile
from pathlib import Path
import numpy as np
import tensorflow as tf
import pandas as pd

from src.config import TEST_MANIFEST
from src.models import build_resnet50_model
from src.preprocessing import load_and_preprocess_image


def test_model_save_and_reload_consistency():
    """Verify saved and reloaded models produce identical predictions."""
    test_df = pd.read_csv(TEST_MANIFEST)
    sample_img_path = test_df.iloc[0]["filepath"]
    img_tensor = tf.expand_dims(load_and_preprocess_image(sample_img_path), axis=0)

    # 1. Build and evaluate original model
    orig_model = build_resnet50_model()
    orig_pred = orig_model(img_tensor, training=False).numpy()

    # 2. Save to temporary location
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_model_path = Path(tmpdir) / "test_model.keras"
        orig_model.save(tmp_model_path)
        assert tmp_model_path.exists(), "Model checkpoint file was not created"

        # 3. Reload in fresh session
        reloaded_model = tf.keras.models.load_model(tmp_model_path)
        reloaded_pred = reloaded_model(img_tensor, training=False).numpy()

        # 4. Assert predictions match exactly
        np.testing.assert_allclose(orig_pred, reloaded_pred, atol=1e-5)
