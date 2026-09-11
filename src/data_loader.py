"""
Dataset discovery, verification, persistent stratified splitting,
manifest generation, class imbalance analysis, and tf.data pipeline creation.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from typing import Dict, Tuple, List, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf

from src.config import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    TRAIN_MANIFEST,
    VAL_MANIFEST,
    TEST_MANIFEST,
    CLASSES,
    CLASS_TO_IDX,
    IMAGE_SIZE,
    BATCH_SIZE,
    RANDOM_SEED,
    VAL_SPLIT_RATIO,
    VALID_EXTENSIONS,
    PLOTS_DIR,
    METRICS_DIR,
)
from src.utils import (
    set_seed,
    verify_image_file,
    compute_file_hash,
    save_json,
    plot_class_distribution,
)
from src.preprocessing import (
    load_and_preprocess_image,
    build_augmentation_layer,
    get_resnet50_preprocess_fn,
)


def inspect_raw_dataset(raw_dir: Path = RAW_DATA_DIR) -> Tuple[pd.DataFrame, List[Dict]]:
    """
    Recursively scan and verify every image in the raw dataset directory.
    Returns: (valid_df, invalid_records)
    """
    valid_records = []
    invalid_records = []

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw dataset directory does not exist at {raw_dir}")

    for file_path in raw_dir.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext not in VALID_EXTENSIONS:
                if ext != ".md" and file_path.name != ".gitkeep":
                    invalid_records.append({
                        "filepath": str(file_path),
                        "reason": f"Unsupported file extension: {ext}"
                    })
                continue

            rel = file_path.relative_to(raw_dir)
            parts = rel.parts
            if len(parts) >= 3:
                split_folder = parts[0]
                class_name = parts[1].lower().strip()
            elif len(parts) == 2:
                split_folder = "Unknown"
                class_name = parts[0].lower().strip()
            else:
                invalid_records.append({
                    "filepath": str(file_path),
                    "reason": "Unexpected folder depth"
                })
                continue

            if class_name not in CLASS_TO_IDX:
                invalid_records.append({
                    "filepath": str(file_path),
                    "reason": f"Unexpected class folder: {class_name}"
                })
                continue

            is_valid, err_msg, dims = verify_image_file(file_path)
            if not is_valid:
                invalid_records.append({
                    "filepath": str(file_path),
                    "reason": err_msg
                })
                continue

            file_hash = compute_file_hash(file_path)
            valid_records.append({
                "filepath": str(file_path.resolve()),
                "relative_path": str(rel),
                "split_folder": split_folder,
                "class_name": class_name,
                "label_idx": CLASS_TO_IDX[class_name],
                "width": dims[0],
                "height": dims[1],
                "format": file_path.suffix.lower().replace(".", "").upper(),
                "sha256": file_hash,
            })

    valid_df = pd.DataFrame(valid_records)
    return valid_df, invalid_records


def create_persistent_splits(
    raw_df: pd.DataFrame,
    processed_dir: Path = PROCESSED_DATA_DIR,
    seed: int = RANDOM_SEED,
    val_ratio: float = VAL_SPLIT_RATIO,
    force_recreate: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generate or load deterministic persistent manifests.
    Guarantees:
    - Official held-out test split is preserved untouched.
    - Zero data leakage between Train, Val, and Test by grouping on cryptographic SHA-256 hash.
    """
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not force_recreate and TRAIN_MANIFEST.exists() and VAL_MANIFEST.exists() and TEST_MANIFEST.exists():
        train_df = pd.read_csv(TRAIN_MANIFEST)
        val_df = pd.read_csv(VAL_MANIFEST)
        test_df = pd.read_csv(TEST_MANIFEST)
        return train_df, val_df, test_df

    has_official_test = (raw_df["split_folder"].str.lower() == "testing").any()

    if has_official_test:
        official_train = raw_df[raw_df["split_folder"].str.lower() == "training"].copy()
        test_df = raw_df[raw_df["split_folder"].str.lower() == "testing"].copy()

        # Group by hash to ensure identical images never leak across train/val
        unique_hashes = official_train.drop_duplicates(subset=["sha256"])[["sha256", "label_idx"]]
        train_hashes, val_hashes = train_test_split(
            unique_hashes["sha256"],
            test_size=val_ratio,
            stratify=unique_hashes["label_idx"],
            random_state=seed
        )
        train_hash_set = set(train_hashes)
        val_hash_set = set(val_hashes)

        train_df = official_train[official_train["sha256"].isin(train_hash_set)].copy()
        val_df = official_train[official_train["sha256"].isin(val_hash_set)].copy()
    else:
        unique_hashes = raw_df.drop_duplicates(subset=["sha256"])[["sha256", "label_idx"]]
        train_hashes, test_val_hashes = train_test_split(
            unique_hashes["sha256"],
            test_size=0.30,
            stratify=unique_hashes["label_idx"],
            random_state=seed
        )
        tv_unique = unique_hashes[unique_hashes["sha256"].isin(set(test_val_hashes))]
        val_hashes, test_hashes = train_test_split(
            tv_unique["sha256"],
            test_size=0.50,
            stratify=tv_unique["label_idx"],
            random_state=seed
        )
        train_df = raw_df[raw_df["sha256"].isin(set(train_hashes))].copy()
        val_df = raw_df[raw_df["sha256"].isin(set(val_hashes))].copy()
        test_df = raw_df[raw_df["sha256"].isin(set(test_hashes))].copy()

    # Save persistent manifests
    train_df.to_csv(TRAIN_MANIFEST, index=False)
    val_df.to_csv(VAL_MANIFEST, index=False)
    test_df.to_csv(TEST_MANIFEST, index=False)

    return train_df, val_df, test_df


def compute_class_weights(train_df: pd.DataFrame) -> Dict[int, float]:
    """Calculate balanced class weights to compensate for any class frequency imbalance."""
    y_train = train_df["label_idx"].values
    unique_classes = np.unique(y_train)
    weights = compute_class_weight(class_weight="balanced", classes=unique_classes, y=y_train)
    return {int(cls): float(weight) for cls, weight in zip(unique_classes, weights)}


def get_dataset_statistics(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    invalid_records: List[Dict]
) -> Dict:
    """Compile comprehensive ground-truth statistics across the dataset."""
    total_valid = len(train_df) + len(val_df) + len(test_df)
    total_discovered = total_valid + len(invalid_records)

    class_distribution = {
        "train": train_df["class_name"].value_counts().to_dict(),
        "val": val_df["class_name"].value_counts().to_dict(),
        "test": test_df["class_name"].value_counts().to_dict(),
    }

    for split in class_distribution:
        for cls in CLASSES:
            if cls not in class_distribution[split]:
                class_distribution[split][cls] = 0

    stats = {
        "total_images_discovered": total_discovered,
        "valid_images_total": total_valid,
        "invalid_or_corrupt_count": len(invalid_records),
        "excluded_details": invalid_records,
        "train_count": len(train_df),
        "validation_count": len(val_df),
        "test_count": len(test_df),
        "class_distribution": class_distribution,
        "formats_present": list(pd.concat([train_df, val_df, test_df])["format"].unique()),
        "class_weights": compute_class_weights(train_df),
    }
    return stats


def parse_image_and_label(filepath: tf.Tensor, label: tf.Tensor, preprocess_fn=None) -> Tuple[tf.Tensor, tf.Tensor]:
    """tf.data worker function to load, decode, resize, and normalize an MRI image."""
    image_bytes = tf.io.read_file(filepath)
    image = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    image = tf.image.resize(image, IMAGE_SIZE)
    image = tf.cast(image, tf.float32)
    if preprocess_fn is None:
        preprocess_fn = get_resnet50_preprocess_fn()
    image = preprocess_fn(image)
    return image, label


def create_tf_dataset(
    manifest_df: pd.DataFrame,
    batch_size: int = BATCH_SIZE,
    is_training: bool = False,
    augment: bool = False,
    preprocess_fn=None,
    subset_size: Optional[int] = None
) -> tf.data.Dataset:
    """Build high-performance tf.data.Dataset from manifest DataFrame."""
    df = manifest_df.copy()
    if subset_size is not None and subset_size < len(df):
        df = df.sample(n=subset_size, random_state=RANDOM_SEED).reset_index(drop=True)

    filepaths = df["filepath"].values
    labels = df["label_idx"].values

    dataset = tf.data.Dataset.from_tensor_slices((filepaths, labels))

    if is_training:
        dataset = dataset.shuffle(buffer_size=min(len(df), 1000), seed=RANDOM_SEED)

    dataset = dataset.map(
        lambda x, y: parse_image_and_label(x, y, preprocess_fn=preprocess_fn),
        num_parallel_calls=tf.data.AUTOTUNE
    )

    if is_training and augment:
        aug_layer = build_augmentation_layer()
        dataset = dataset.map(
            lambda x, y: (aug_layer(x, training=True), y),
            num_parallel_calls=tf.data.AUTOTUNE
        )

    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE)
    return dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset Inspection & Splitting Tool")
    parser.add_argument("--inspect", action="store_true", help="Inspect raw dataset and generate manifest/stats")
    parser.add_argument("--force-resplit", action="store_true", help="Force re-generation of split manifests")
    args = parser.parse_args()

    set_seed(RANDOM_SEED)
    print("Scanning and verifying MRI dataset...")
    valid_df, invalid_records = inspect_raw_dataset()
    print(f"Discovered: {len(valid_df)} valid images, {len(invalid_records)} invalid/corrupt images.")

    print("Generating persistent split manifests...")
    train_df, val_df, test_df = create_persistent_splits(
        valid_df, force_recreate=args.force_resplit
    )

    stats = get_dataset_statistics(train_df, val_df, test_df, invalid_records)
    
    stats_file = METRICS_DIR / "dataset_statistics.json"
    save_json(stats, stats_file)
    print(f"Saved dataset statistics to: {stats_file}")

    dist_plot_path = PLOTS_DIR / "class_distribution.png"
    plot_class_distribution(stats["class_distribution"], dist_plot_path)
    print(f"Generated class distribution plot at: {dist_plot_path}")

    print("\n" + "=" * 55)
    print("DATASET VERIFICATION & SPLIT SUMMARY")
    print("=" * 55)
    print(f"Total Discovered Images : {stats['total_images_discovered']}")
    print(f"Valid Images Total      : {stats['valid_images_total']}")
    print(f"Corrupted/Invalid Files : {stats['invalid_or_corrupt_count']}")
    print(f"Training Split Count    : {stats['train_count']}")
    print(f"Validation Split Count  : {stats['validation_count']}")
    print(f"Held-out Test Count     : {stats['test_count']}")
    print("-" * 55)
    print("Class Frequencies per Split:")
    for cls in CLASSES:
        tr = stats["class_distribution"]["train"][cls]
        vl = stats["class_distribution"]["val"][cls]
        ts = stats["class_distribution"]["test"][cls]
        print(f"  {cls:<12} | Train: {tr:4d} | Val: {vl:4d} | Test: {ts:4d} | Total: {tr+vl+ts:4d}")
    print("-" * 55)
    print("Computed Training Class Weights (Balanced):")
    for cls_idx, wt in stats["class_weights"].items():
        print(f"  Class {cls_idx} ({CLASSES[cls_idx]:<11}): {wt:.4f}")
    print("=" * 55)
