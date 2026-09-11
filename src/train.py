"""
Reusable training pipeline for ResNet50 Transfer Learning on Brain Tumor MRI images.
Supports Stage A (Smoke Test on tiny subset) and Stage B (Full Experiment on all valid images).
Logs actual training history, saves best checkpoints, generates curves, and evaluates on test set.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
import time
from typing import Dict, Any, Optional

import numpy as np
import pandas as pd
import tensorflow as tf

from src.config import (
    TRAIN_MANIFEST,
    VAL_MANIFEST,
    BEST_MODEL_PATH,
    MODELS_DIR,
    LOGS_DIR,
    PLOTS_DIR,
    BATCH_SIZE,
    EPOCHS,
    LEARNING_RATE,
    EARLY_STOPPING_PATIENCE,
    REDUCE_LR_PATIENCE,
    REDUCE_LR_FACTOR,
    MIN_LR,
    RANDOM_SEED,
)
from src.utils import (
    set_seed,
    save_json,
    plot_training_history,
    detect_hardware,
)
from src.data_loader import create_tf_dataset, compute_class_weights
from src.models import build_resnet50_model
from src.evaluate import run_full_evaluation


def train_resnet50(
    train_manifest: Path = TRAIN_MANIFEST,
    val_manifest: Path = VAL_MANIFEST,
    model_save_path: Path = BEST_MODEL_PATH,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    is_smoke_test: bool = False,
    smoke_subset_size: int = 16
) -> Dict[str, Any]:
    """
    Execute training workflow for ResNet50 transfer learning.
    """
    set_seed(RANDOM_SEED)
    hardware_info = detect_hardware()

    prefix = "[SMOKE TEST]" if is_smoke_test else "[FULL EXPERIMENT]"
    print("\n" + "=" * 65)
    print(f"{prefix} STARTING RESNET50 TRAINING PIPELINE")
    print("=" * 65)
    print(f"Device detected: {hardware_info['primary_device']} (GPU available: {hardware_info['gpu_available']})")
    print(f"TensorFlow version: {hardware_info['tf_version']}")

    # 1. Load manifests
    if not train_manifest.exists() or not val_manifest.exists():
        raise FileNotFoundError(
            f"Dataset manifests missing. Run 'python -m src.data_loader --inspect' first."
        )

    train_df = pd.read_csv(train_manifest)
    val_df = pd.read_csv(val_manifest)

    train_subset = smoke_subset_size if is_smoke_test else None
    val_subset = max(8, smoke_subset_size // 2) if is_smoke_test else None

    # 2. Build tf.data pipelines
    print(f"\nPreparing datasets ({'Smoke Test sample' if is_smoke_test else 'Full Dataset'})...")
    train_ds = create_tf_dataset(
        train_df,
        batch_size=batch_size,
        is_training=True,
        augment=True,
        subset_size=train_subset
    )
    val_ds = create_tf_dataset(
        val_df,
        batch_size=batch_size,
        is_training=False,
        augment=False,
        subset_size=val_subset
    )

    actual_train_count = train_subset if is_smoke_test else len(train_df)
    actual_val_count = val_subset if is_smoke_test else len(val_df)
    print(f"Training samples: {actual_train_count}")
    print(f"Validation samples: {actual_val_count}")

    # Compute class weights
    class_weights = compute_class_weights(train_df) if not is_smoke_test else None
    if class_weights:
        print(f"Class weights enabled: {class_weights}")

    # 3. Build Model
    print("\nBuilding ResNet50 transfer learning model (Frozen backbone)...")
    model = build_resnet50_model(learning_rate=learning_rate)

    # 4. Callbacks
    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=str(model_save_path),
        monitor="val_loss",
        mode="min",
        save_best_only=True,
        verbose=1
    )
    callbacks = [checkpoint_callback]

    if not is_smoke_test:
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            mode="min",
            patience=EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        )
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            mode="min",
            factor=REDUCE_LR_FACTOR,
            patience=REDUCE_LR_PATIENCE,
            min_lr=MIN_LR,
            verbose=1
        )
        callbacks.extend([early_stopping, reduce_lr])

    actual_epochs = 2 if is_smoke_test else epochs
    print(f"\nBeginning training for up to {actual_epochs} epochs...")

    start_time = time.time()
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=actual_epochs,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    duration_seconds = time.time() - start_time

    history_dict = {k: [float(v) for v in vals] for k, vals in history.history.items()}
    best_epoch = int(np.argmin(history_dict["val_loss"])) + 1
    best_val_loss = float(min(history_dict["val_loss"]))
    best_val_acc = float(history_dict["val_accuracy"][best_epoch - 1])

    summary_info = {
        "pipeline_mode": "smoke_test" if is_smoke_test else "full_experiment",
        "model_name": model.name,
        "epochs_trained": len(history_dict["loss"]),
        "best_epoch": best_epoch,
        "best_val_loss": best_val_loss,
        "best_val_accuracy": best_val_acc,
        "duration_seconds": round(duration_seconds, 2),
        "duration_formatted": f"{int(duration_seconds // 60)}m {int(duration_seconds % 60)}s",
        "saved_model_path": str(model_save_path.resolve()),
        "hyperparameters": {
            "batch_size": batch_size,
            "initial_learning_rate": learning_rate,
            "max_epochs": actual_epochs,
            "optimizer": "Adam",
            "loss": "sparse_categorical_crossentropy"
        },
        "history": history_dict,
        "hardware": hardware_info
    }

    # Save log
    if not is_smoke_test:
        history_file = LOGS_DIR / "resnet50_training_history.json"
        save_json(summary_info, history_file)
        print(f"\nSaved training history to {history_file}")

        # Plot curves
        acc_plot, loss_plot = plot_training_history(history_dict, PLOTS_DIR)
        print(f"Generated accuracy plot: {acc_plot}")
        print(f"Generated loss plot: {loss_plot}")

    print("\n" + "=" * 65)
    print(f"{prefix} TRAINING COMPLETED IN {summary_info['duration_formatted']}")
    print(f"Best Epoch: {best_epoch} | Best Val Loss: {best_val_loss:.4f} | Best Val Acc: {best_val_acc*100:.2f}%")
    print("=" * 65)

    return summary_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ResNet50 Brain Tumor Classifier")
    parser.add_argument("--smoke-test", action="store_true", help="Run quick smoke test on 16 images")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Training batch size")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Initial learning rate")
    args = parser.parse_args()

    if args.smoke_test:
        smoke_model_path = MODELS_DIR / "resnet50_smoke.keras"
        train_resnet50(
            model_save_path=smoke_model_path,
            is_smoke_test=True
        )
    else:
        # Full training on all valid training images
        train_resnet50(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            is_smoke_test=False
        )
        # Evaluate on held-out test set
        run_full_evaluation(BEST_MODEL_PATH)
