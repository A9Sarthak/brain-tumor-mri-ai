"""
Reusable two-stage training pipeline for Transfer Learning on Brain Tumor MRI images.
Supports EfficientNet-B0 and other architectures.
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
    MODEL_PATHS,
)
from src.utils import (
    set_seed,
    save_json,
    plot_training_history,
    detect_hardware,
)
from src.data_loader import create_tf_dataset, compute_class_weights
from src.models import build_model
from src.evaluate import run_full_evaluation
from src.preprocessing import get_model_preprocess_fn

def unfreeze_model_top_layers(model: tf.keras.Model, unfreeze_count: int = 40) -> tf.keras.Model:
    """Unfreeze the top N backbone layers for fine-tuning, keeping BatchNorm layers frozen."""
    head_names = {"global_average_pooling", "dense_feature_head", "batch_norm", "head_dropout", "classification_output"}
    backbone_layers = [l for l in model.layers if l.name not in head_names]
    
    freeze_until = max(0, len(backbone_layers) - unfreeze_count)
    for i, layer in enumerate(backbone_layers):
        if i < freeze_until:
            layer.trainable = False
        else:
            if isinstance(layer, tf.keras.layers.BatchNormalization):
                layer.trainable = False
            else:
                layer.trainable = True
                
    for layer in model.layers:
        if layer.name in head_names and not isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = True
            
    trainable_count = sum(1 for l in model.layers if l.trainable)
    print(f"Unfrozen top {len(backbone_layers) - freeze_until} backbone layers. Total trainable layers in model: {trainable_count}")
    return model

def train_model(
    arch_name: str = "EfficientNet-B0",
    train_manifest: Path = TRAIN_MANIFEST,
    val_manifest: Path = VAL_MANIFEST,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
    learning_rate: float = LEARNING_RATE,
    is_smoke_test: bool = False,
    smoke_subset_size: int = 16
) -> Dict[str, Any]:
    
    set_seed(RANDOM_SEED)
    hardware_info = detect_hardware()

    model_save_path = MODEL_PATHS.get(arch_name, MODELS_DIR / f"{arch_name.lower()}_best.keras")
    canonical_model_path = MODELS_DIR / "best_efficientnet_model.keras"
    if is_smoke_test:
        model_save_path = MODELS_DIR / f"{arch_name.lower()}_smoke.keras"

    prefix = "[SMOKE TEST]" if is_smoke_test else "[FULL EXPERIMENT]"
    print("\n" + "=" * 65)
    print(f"{prefix} STARTING {arch_name} TWO-STAGE TRAINING PIPELINE")
    print("=" * 65)
    print(f"Device detected: {hardware_info['primary_device']} (GPU available: {hardware_info['gpu_available']})")

    # 1. Load manifests
    if not train_manifest.exists() or not val_manifest.exists():
        raise FileNotFoundError("Dataset manifests missing. Run 'python -m src.data_loader --inspect' first.")

    train_df = pd.read_csv(train_manifest)
    val_df = pd.read_csv(val_manifest)

    train_subset = smoke_subset_size if is_smoke_test else None
    val_subset = max(8, smoke_subset_size // 2) if is_smoke_test else None

    # 2. Build tf.data pipelines
    print(f"\nPreparing datasets ({'Smoke Test sample' if is_smoke_test else 'Full Dataset'})...")
    preprocess_fn = get_model_preprocess_fn(arch_name)
    train_ds = create_tf_dataset(
        train_df, batch_size=batch_size, is_training=True, augment=True, 
        preprocess_fn=preprocess_fn, subset_size=train_subset
    )
    val_ds = create_tf_dataset(
        val_df, batch_size=batch_size, is_training=False, augment=False, 
        preprocess_fn=preprocess_fn, subset_size=val_subset
    )

    actual_train_count = train_subset if is_smoke_test else len(train_df)
    actual_val_count = val_subset if is_smoke_test else len(val_df)
    print(f"Training samples: {actual_train_count}")
    print(f"Validation samples: {actual_val_count}")

    class_weights = compute_class_weights(train_df) if not is_smoke_test else None

    # 3. Build Model (Stage 1)
    print(f"\nBuilding {arch_name} transfer learning model (Frozen backbone)...")
    model = build_model(architecture_name=arch_name, freeze_backbone=True, learning_rate=learning_rate)

    model_save_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 4. Stage 1: Train Head Only
    stage1_epochs = 2 if is_smoke_test else 4
    print(f"\n--- STAGE 1: Training Classification Head for {stage1_epochs} epochs ---")
    start_time = time.time()
    
    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=stage1_epochs,
        class_weight=class_weights,
        verbose=1
    )
    
    # 5. Stage 2: Fine-Tuning
    print("\n--- STAGE 2: Fine-Tuning Top Backbone Layers ---")
    model = unfreeze_model_top_layers(model, unfreeze_count=40)
    
    # Recompile with much smaller learning rate
    fine_tune_lr = 1e-5
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=fine_tune_lr),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    
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
            monitor="val_loss", patience=EARLY_STOPPING_PATIENCE, restore_best_weights=True, verbose=1
        )
        reduce_lr_cb = tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=REDUCE_LR_FACTOR, patience=REDUCE_LR_PATIENCE, min_lr=MIN_LR, verbose=1
        )
        callbacks.extend([early_stopping, reduce_lr_cb])

    stage2_epochs = 2 if is_smoke_test else max(4, epochs - stage1_epochs)
    total_target_epochs = stage1_epochs + stage2_epochs
    print(f"Beginning fine-tuning for up to {stage2_epochs} epochs (epochs {stage1_epochs+1} to {total_target_epochs}) with LR={fine_tune_lr}...")
    
    history_stage2 = model.fit(
        train_ds,
        validation_data=val_ds,
        initial_epoch=stage1_epochs,
        epochs=total_target_epochs,
        callbacks=callbacks,
        class_weight=class_weights,
        verbose=1
    )
    
    duration_seconds = time.time() - start_time
    
    # Merge histories
    history_dict = {k: [float(v) for v in vals] for k, vals in history_stage1.history.items()}
    for k, vals in history_stage2.history.items():
        if k in history_dict:
            history_dict[k].extend([float(v) for v in vals])
        else:
            history_dict[k] = [float(v) for v in vals]

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
            "stage1_lr": learning_rate,
            "stage2_lr": fine_tune_lr,
            "stage1_epochs": stage1_epochs,
            "stage2_epochs": stage2_epochs,
            "optimizer": "Adam",
        },
        "history": history_dict,
        "hardware": hardware_info
    }

    if not is_smoke_test:
        # Copy to canonical final model path
        import shutil
        if model_save_path.exists():
            shutil.copyfile(model_save_path, canonical_model_path)
            print(f"Copied best model to canonical path: {canonical_model_path}")

        history_file = LOGS_DIR / f"{arch_name.lower()}_training_history.json"
        save_json(summary_info, history_file)
        print(f"\nSaved training history to {history_file}")

        acc_plot, loss_plot = plot_training_history(history_dict, PLOTS_DIR, arch_name=arch_name)
        print(f"Generated accuracy plot: {acc_plot}")
        print(f"Generated loss plot: {loss_plot}")

    print("\n" + "=" * 65)
    print(f"{prefix} TRAINING COMPLETED IN {summary_info['duration_formatted']}")
    print(f"Best Val Acc: {best_val_acc*100:.2f}% | Best Val Loss: {best_val_loss:.4f}")
    print("=" * 65)

    return summary_info


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Brain Tumor Classifier")
    parser.add_argument("--arch", type=str, default="EfficientNet-B0", help="Architecture to use")
    parser.add_argument("--smoke-test", action="store_true", help="Run quick smoke test on 16 images")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Training batch size")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Initial learning rate")
    args = parser.parse_args()

    train_model(
        arch_name=args.arch,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        is_smoke_test=args.smoke_test
    )
    
    if not args.smoke_test:
        model_path = MODEL_PATHS.get(args.arch, MODELS_DIR / f"{args.arch.lower()}_best.keras")
        # In evaluate.py, run_full_evaluation accepts model_path as arg but we also need to make sure
        # preprocess_fn is passed or evaluate knows which arch we are using.
        run_full_evaluation(model_path)
