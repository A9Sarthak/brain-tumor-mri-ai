"""
Comprehensive model evaluation, baseline comparison, metrics calculation,
and programmatic confusion matrix visualization.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Tuple
import argparse
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

from src.config import (
    TEST_MANIFEST,
    TRAIN_MANIFEST,
    CLASSES,
    CLASS_DISPLAY_NAMES,
    BEST_MODEL_PATH,
    METRICS_DIR,
    CONFUSION_MATRICES_DIR,
    BATCH_SIZE,
)
from src.utils import (
    save_json,
    plot_confusion_matrix_heatmap,
    detect_hardware,
)
from src.data_loader import create_tf_dataset
from src.preprocessing import get_model_preprocess_fn

def evaluate_majority_baseline(
    train_manifest: Path = TRAIN_MANIFEST,
    test_manifest: Path = TEST_MANIFEST
) -> dict:
    """
    Academic baseline: Naively predicts the most frequent class from training data.
    Provides a quantitative benchmark to isolate the true value-add of deep transfer learning.
    """
    train_df = pd.read_csv(train_manifest)
    test_df = pd.read_csv(test_manifest)

    majority_class_idx = int(train_df["label_idx"].mode()[0])
    y_true = test_df["label_idx"].values
    y_pred = np.full_like(y_true, fill_value=majority_class_idx)

    baseline_metrics = {
        "model_name": "Majority-Class Naive Baseline",
        "predicted_class_index": majority_class_idx,
        "predicted_class_name": CLASSES[majority_class_idx],
        "test_sample_count": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
        "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }
    return baseline_metrics


def evaluate_model_on_test_set(
    model: tf.keras.Model,
    arch_name: str = "EfficientNet-B0",
    test_manifest: Path = TEST_MANIFEST,
    batch_size: int = BATCH_SIZE
) -> Tuple[dict, np.ndarray, np.ndarray]:
    """
    Run full inference on held-out test split and calculate comprehensive multiclass metrics.
    """
    test_df = pd.read_csv(test_manifest)
    preprocess_fn = get_model_preprocess_fn(arch_name)
    test_ds = create_tf_dataset(test_df, batch_size=batch_size, is_training=False, augment=False, preprocess_fn=preprocess_fn)

    print(f"Running inference across held-out test split for {arch_name}...")
    y_probs = model.predict(test_ds, verbose=1)
    y_pred = np.argmax(y_probs, axis=1)
    y_true = test_df["label_idx"].values

    # Add prediction distribution logging
    display_names = [CLASS_DISPLAY_NAMES[c] for c in CLASSES]
    unique, counts = np.unique(y_pred, return_counts=True)
    pred_dist = {CLASS_DISPLAY_NAMES[CLASSES[i]]: int(c) for i, c in zip(unique, counts)}
    for name in display_names:
        if name not in pred_dist:
            pred_dist[name] = 0
    print(f"\nPrediction count by class: {pred_dist}")

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    report_dict = classification_report(
        y_true,
        y_pred,
        target_names=display_names,
        output_dict=True,
        zero_division=0
    )
    report_text = classification_report(
        y_true,
        y_pred,
        target_names=display_names,
        zero_division=0
    )

    metrics = {
        "model_name": model.name,
        "architecture": arch_name,
        "test_sample_count": int(len(y_true)),
        "prediction_distribution": pred_dist,
        "accuracy": acc,
        "precision_macro": prec_macro,
        "precision_weighted": prec_weighted,
        "recall_macro": rec_macro,
        "recall_weighted": rec_weighted,
        "f1_macro": f1_macro,
        "f1_weighted": f1_weighted,
        "per_class_report": report_dict,
        "classification_report_text": report_text,
        "device_info": detect_hardware()
    }

    return metrics, y_true, y_pred


def run_full_evaluation(model_path: Path = BEST_MODEL_PATH) -> dict:
    """Execute complete evaluation workflow, save metrics and plot confusion matrix."""
    if not model_path.exists():
        raise FileNotFoundError(f"Model checkpoint not found at {model_path}")

    # Infer arch from filename
    filename = model_path.stem.lower()
    if "efficientnet" in filename:
        arch_name = "EfficientNet-B0"
    elif "mobilenet" in filename:
        arch_name = "MobileNetV2"
    elif "vgg" in filename:
        arch_name = "VGG16"
    else:
        arch_name = "ResNet50"

    print(f"Loading {arch_name} model checkpoint from {model_path}...")
    model = tf.keras.models.load_model(model_path)

    # 1. Baseline Evaluation
    print("\n--- Evaluating Baseline Model ---")
    baseline_metrics = evaluate_majority_baseline()
    baseline_file = METRICS_DIR / "baseline_metrics.json"
    save_json(baseline_metrics, baseline_file)
    print(f"Baseline Accuracy: {baseline_metrics['accuracy']:.4f}")

    # 2. Model Evaluation
    print(f"\n--- Evaluating {arch_name} on Held-out Test Set ---")
    metrics, y_true, y_pred = evaluate_model_on_test_set(model, arch_name=arch_name)

    # Save Metrics
    metrics_file = METRICS_DIR / f"{arch_name.lower()}_test_metrics.json"
    save_json(metrics, metrics_file)

    report_txt_file = METRICS_DIR / f"{arch_name.lower()}_classification_report.txt"
    with open(report_txt_file, "w", encoding="utf-8") as f:
        f.write(metrics["classification_report_text"])

    # 3. Generate Confusion Matrix Plot
    cm_path = CONFUSION_MATRICES_DIR / f"{arch_name.lower()}_confusion_matrix.png"
    display_names = [CLASS_DISPLAY_NAMES[c] for c in CLASSES]
    plot_confusion_matrix_heatmap(y_true, y_pred, display_names, cm_path, title=f"{arch_name} Confusion Matrix (Held-out Test Set)")
    print(f"Saved confusion matrix plot to: {cm_path}")

    # Summary Output
    print("\n" + "=" * 60)
    print("HELD-OUT TEST SET EVALUATION SUMMARY")
    print("=" * 60)
    print(f"{'Metric':<25} | {'Baseline':<14} | {arch_name:<14}")
    print("-" * 60)
    print(f"{'Accuracy':<25} | {baseline_metrics['accuracy']*100:6.2f}%       | {metrics['accuracy']*100:6.2f}%")
    print(f"{'Macro Precision':<25} | {baseline_metrics['precision_macro']*100:6.2f}%       | {metrics['precision_macro']*100:6.2f}%")
    print(f"{'Weighted Precision':<25} | {baseline_metrics['precision_weighted']*100:6.2f}%       | {metrics['precision_weighted']*100:6.2f}%")
    print(f"{'Macro Recall':<25} | {baseline_metrics['recall_macro']*100:6.2f}%       | {metrics['recall_macro']*100:6.2f}%")
    print(f"{'Weighted Recall':<25} | {baseline_metrics['recall_weighted']*100:6.2f}%       | {metrics['recall_weighted']*100:6.2f}%")
    print(f"{'Macro F1-Score':<25} | {baseline_metrics['f1_macro']*100:6.2f}%       | {metrics['f1_macro']*100:6.2f}%")
    print(f"{'Weighted F1-Score':<25} | {baseline_metrics['f1_weighted']*100:6.2f}%       | {metrics['f1_weighted']*100:6.2f}%")
    print("=" * 60)
    print("\nClassification Report:\n")
    print(metrics["classification_report_text"])
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Brain Tumor Classifier")
    parser.add_argument("--model-path", type=str, default=str(BEST_MODEL_PATH), help="Path to trained model")
    args = parser.parse_args()

    run_full_evaluation(Path(args.model_path))
