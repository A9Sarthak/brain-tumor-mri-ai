"""
Automated tests for dataset split isolation and zero data leakage.
Verifies disjoint sets across Train, Validation, and Held-out Test partitions
by checking relative file paths and cryptographic SHA-256 hashes.
"""
import pytest
import pandas as pd
from src.config import TRAIN_MANIFEST, VAL_MANIFEST, TEST_MANIFEST


@pytest.fixture(scope="module")
def manifests():
    assert TRAIN_MANIFEST.exists(), "Train manifest must exist"
    assert VAL_MANIFEST.exists(), "Validation manifest must exist"
    assert TEST_MANIFEST.exists(), "Test manifest must exist"
    
    train_df = pd.read_csv(TRAIN_MANIFEST)
    val_df = pd.read_csv(VAL_MANIFEST)
    test_df = pd.read_csv(TEST_MANIFEST)
    return train_df, val_df, test_df


def test_manifests_non_empty(manifests):
    train_df, val_df, test_df = manifests
    assert len(train_df) > 0, "Train split cannot be empty"
    assert len(val_df) > 0, "Validation split cannot be empty"
    assert len(test_df) > 0, "Test split cannot be empty"


def test_no_filepath_leakage_between_splits(manifests):
    """Ensure no overlapping image paths between any partitions."""
    train_df, val_df, test_df = manifests
    
    train_paths = set(train_df["relative_path"])
    val_paths = set(val_df["relative_path"])
    test_paths = set(test_df["relative_path"])
    
    train_val_overlap = train_paths.intersection(val_paths)
    train_test_overlap = train_paths.intersection(test_paths)
    val_test_overlap = val_paths.intersection(test_paths)
    
    assert len(train_val_overlap) == 0, f"Train-Val path leakage detected: {len(train_val_overlap)} files"
    assert len(train_test_overlap) == 0, f"Train-Test path leakage detected: {len(train_test_overlap)} files"
    assert len(val_test_overlap) == 0, f"Val-Test path leakage detected: {len(val_test_overlap)} files"


def test_no_hash_leakage_between_splits(manifests):
    """Ensure no duplicate image content (identical SHA-256) across partitions."""
    train_df, val_df, test_df = manifests
    
    train_hashes = set(train_df["sha256"])
    val_hashes = set(val_df["sha256"])
    test_hashes = set(test_df["sha256"])
    
    train_val_hash_overlap = train_hashes.intersection(val_hashes)
    train_test_hash_overlap = train_hashes.intersection(test_hashes)
    val_test_hash_overlap = val_hashes.intersection(test_hashes)
    
    assert len(train_val_hash_overlap) == 0, f"Train-Val content hash duplicate: {len(train_val_hash_overlap)}"
    assert len(train_test_hash_overlap) == 0, f"Train-Test content hash duplicate: {len(train_test_hash_overlap)}"
    assert len(val_test_hash_overlap) == 0, f"Val-Test content hash duplicate: {len(val_test_hash_overlap)}"


def test_split_totals_equal_full_dataset(manifests):
    """Ensure sum of split partitions strictly equals total verified images."""
    train_df, val_df, test_df = manifests
    total_split_count = len(train_df) + len(val_df) + len(test_df)
    assert total_split_count == 7200, f"Expected 7200 images, got {total_split_count}"
