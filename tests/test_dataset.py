"""
Automated unit and integration tests for dataset integrity,
class discovery, and corruption handling.
"""
import pytest
from pathlib import Path
import pandas as pd
from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    CLASSES,
    CLASS_TO_IDX,
    TRAIN_MANIFEST,
    VAL_MANIFEST,
    TEST_MANIFEST,
)
from src.utils import verify_image_file


def test_expected_classes():
    """Verify that all four target classes exist in configuration."""
    assert len(CLASSES) == 4
    assert set(CLASSES) == {"glioma", "meningioma", "notumor", "pituitary"}
    for cls in CLASSES:
        assert cls in CLASS_TO_IDX


def test_raw_dataset_structure_exists():
    """Verify raw dataset folders exist with official splits."""
    assert RAW_DATA_DIR.exists(), f"Raw data dir missing: {RAW_DATA_DIR}"
    assert (RAW_DATA_DIR / "Training").exists(), "Raw Training folder missing"
    assert (RAW_DATA_DIR / "Testing").exists(), "Raw Testing folder missing"

    for cls in CLASSES:
        assert (RAW_DATA_DIR / "Training" / cls).exists(), f"Training class folder missing: {cls}"
        assert (RAW_DATA_DIR / "Testing" / cls).exists(), f"Testing class folder missing: {cls}"


def test_manifest_files_exist_and_valid():
    """Verify persistent CSV manifests exist with proper schema."""
    assert TRAIN_MANIFEST.exists()
    assert VAL_MANIFEST.exists()
    assert TEST_MANIFEST.exists()

    expected_columns = {"filepath", "relative_path", "class_name", "label_idx", "width", "height", "format", "sha256"}
    for manifest_path in [TRAIN_MANIFEST, VAL_MANIFEST, TEST_MANIFEST]:
        df = pd.read_csv(manifest_path)
        assert len(df) > 0
        assert expected_columns.issubset(set(df.columns))
        # Ensure all labels are within [0, 3]
        assert set(df["label_idx"].unique()).issubset({0, 1, 2, 3})


def test_no_corrupted_images_in_manifests():
    """Sample images from manifests and ensure they decode properly."""
    for manifest_path in [TRAIN_MANIFEST, VAL_MANIFEST, TEST_MANIFEST]:
        df = pd.read_csv(manifest_path).sample(n=min(10, len(pd.read_csv(manifest_path))), random_state=42)
        for _, row in df.iterrows():
            filepath = Path(row["filepath"])
            assert filepath.exists()
            is_valid, err, dims = verify_image_file(filepath)
            assert is_valid, f"Corrupted image in manifest: {filepath} ({err})"
            assert dims[0] > 0 and dims[1] > 0
