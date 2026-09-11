"""
Utility functions for logging, reproducibility, hardware detection,
image verification, and metric visualizations.
"""
import os
import random
import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CLI rendering
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix


def set_seed(seed: int = 42) -> None:
    """Ensure determinism across python, numpy, and tensorflow."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)


def detect_hardware() -> Dict[str, Any]:
    """Detect actual hardware devices available for TensorFlow execution."""
    physical_devices = tf.config.list_physical_devices()
    gpus = tf.config.list_physical_devices("GPU")
    has_gpu = len(gpus) > 0
    device_name = gpus[0].name if has_gpu else "CPU"
    
    info = {
        "physical_devices": [d.name for d in physical_devices],
        "gpu_available": has_gpu,
        "gpu_count": len(gpus),
        "primary_device": device_name,
        "tf_version": tf.__version__,
    }
    return info


def compute_file_hash(filepath: Path) -> str:
    """Compute SHA-256 hash of a file for integrity and duplicate detection."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def verify_image_file(filepath: Path) -> Tuple[bool, Optional[str], Optional[Tuple[int, int]]]:
    """
    Verify that an image file exists, is non-empty, and can be read and decoded.
    Returns: (is_valid, error_reason, (width, height))
    """
    if not filepath.exists():
        return False, "File does not exist", None
    
    if filepath.stat().st_size == 0:
        return False, "Zero-byte file", None

    try:
        with Image.open(filepath) as img:
            img.verify()
        # Re-open to read dimensions and test decoding
        with Image.open(filepath) as img:
            img.load()
            dims = img.size  # (width, height)
            format_name = img.format
            if format_name not in ["JPEG", "PNG"]:
                return False, f"Unsupported format: {format_name}", None
            return True, None, dims
    except Exception as e:
        return False, f"Corrupt image: {str(e)}", None


def save_json(data: Any, filepath: Path) -> None:
    """Save serializable data to formatted JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_json(filepath: Path) -> Any:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_class_distribution(distribution_data: Dict[str, Dict[str, int]], output_path: Path) -> None:
    """
    Plot grouped bar chart of class distributions across train, val, and test splits.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    classes = list(next(iter(distribution_data.values())).keys())
    splits = list(distribution_data.keys())
    
    x = np.arange(len(classes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2b5c8f", "#3a9679", "#d66853"]
    
    for i, (split, color) in enumerate(zip(splits, colors)):
        counts = [distribution_data[split][cls] for cls in classes]
        offset = (i - 1) * width
        rects = ax.bar(x + offset, counts, width, label=split.capitalize(), color=color, alpha=0.85)
        ax.bar_label(rects, padding=3, fontsize=9)
    
    ax.set_ylabel("Number of MRI Images", fontsize=12, fontweight="bold")
    ax.set_title("Brain Tumor MRI Class Distribution Across Splits", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels([c.capitalize() for c in classes], fontsize=11, fontweight="semibold")
    ax.legend(frameon=True, fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


def plot_training_history(history: Dict[str, list], output_dir: Path) -> Tuple[Path, Path]:
    """
    Plot and save training/validation accuracy and loss curves programmatically.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    epochs = range(1, len(history["accuracy"]) + 1)
    
    # 1. Accuracy Curve
    acc_path = output_dir / "resnet50_accuracy.png"
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["accuracy"], "o-", label="Training Accuracy", color="#1f77b4", linewidth=2)
    if "val_accuracy" in history:
        plt.plot(epochs, history["val_accuracy"], "s-", label="Validation Accuracy", color="#ff7f0e", linewidth=2)
    plt.title("ResNet50 Classification Accuracy vs. Epochs", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Accuracy", fontsize=11)
    plt.legend(frameon=True, loc="lower right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(acc_path, dpi=300)
    plt.close()
    
    # 2. Loss Curve
    loss_path = output_dir / "resnet50_loss.png"
    plt.figure(figsize=(8, 5))
    plt.plot(epochs, history["loss"], "o-", label="Training Loss", color="#1f77b4", linewidth=2)
    if "val_loss" in history:
        plt.plot(epochs, history["val_loss"], "s-", label="Validation Loss", color="#d62728", linewidth=2)
    plt.title("ResNet50 Categorical Cross-Entropy Loss vs. Epochs", fontsize=13, fontweight="bold")
    plt.xlabel("Epoch", fontsize=11)
    plt.ylabel("Loss", fontsize=11)
    plt.legend(frameon=True, loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(loss_path, dpi=300)
    plt.close()
    
    return acc_path, loss_path


def plot_confusion_matrix_heatmap(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    class_names: list,
    output_path: Path,
    title: str = "ResNet50 Confusion Matrix (Held-out Test Set)"
) -> Path:
    """
    Compute and plot programmatic heatmap confusion matrix with counts and percentages.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=[c.capitalize() for c in class_names],
        yticklabels=[c.capitalize() for c in class_names],
        title=title,
        ylabel="True Class",
        xlabel="Predicted Class"
    )
    
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
    
    # Annotate counts and percentages
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            count = cm[i, j]
            pct = cm_norm[i, j] * 100
            ax.text(
                j, i, f"{count}\n({pct:.1f}%)",
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=10, fontweight="bold"
            )
            
    fig.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    return output_path
