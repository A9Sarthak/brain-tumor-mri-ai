"""
Automated unit tests for image preprocessing, resizing, normalization,
and data augmentation pipelines.
"""
import pytest
import numpy as np
import tensorflow as tf
from pathlib import Path
import pandas as pd

from src.config import TEST_MANIFEST, IMAGE_SIZE, INPUT_SHAPE
from src.preprocessing import (
    load_and_preprocess_image,
    preprocess_image_tensor,
    build_augmentation_layer,
    get_resnet50_preprocess_fn,
)


@pytest.fixture
def sample_image_path():
    test_df = pd.read_csv(TEST_MANIFEST)
    return test_df.iloc[0]["filepath"]


def test_load_and_preprocess_image(sample_image_path):
    """Verify loading from disk produces correct shape and non-zero float values."""
    tensor = load_and_preprocess_image(sample_image_path, target_size=IMAGE_SIZE)
    assert isinstance(tensor, tf.Tensor)
    assert tensor.shape == (224, 224, 3)
    assert tensor.dtype == tf.float32
    # Check that tensor has non-zero values
    assert tf.reduce_sum(tf.abs(tensor)).numpy() > 0


def test_resnet50_preprocessing_zero_centered():
    """Verify ResNet50 preprocessing centers around ImageNet channel means."""
    dummy_img = tf.ones((224, 224, 3), dtype=tf.float32) * 200.0
    preproc_fn = get_resnet50_preprocess_fn()
    processed = preproc_fn(dummy_img)
    assert processed.shape == (224, 224, 3)
    # ResNet50 preproc subtracts channel means (~103.939, 116.779, 123.68)
    assert tf.reduce_mean(processed).numpy() < 200.0


def test_augmentation_layer_preserves_shape():
    """Verify data augmentation preserves tensor shape and float32 type."""
    aug_layer = build_augmentation_layer()
    dummy_batch = tf.random.uniform((4, 224, 224, 3), minval=0.0, maxval=255.0, dtype=tf.float32)
    augmented = aug_layer(dummy_batch, training=True)
    assert augmented.shape == (4, 224, 224, 3)
    assert augmented.dtype == tf.float32
