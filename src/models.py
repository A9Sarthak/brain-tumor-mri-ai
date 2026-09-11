"""
Transfer Learning Model Architecture for Brain Tumor MRI Classification.
Implements ResNet50 backbone with ImageNet pretrained weights and custom classification head.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Tuple
import tensorflow as tf
from src.config import INPUT_SHAPE, NUM_CLASSES, LEARNING_RATE


def build_resnet50_model(
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """
    Build and compile ResNet50 transfer learning model for 4-class MRI classification.
    
    Architecture:
    Input MRI (224x224x3)
    ↓
    Pretrained ResNet50 backbone (ImageNet weights, include_top=False)
    ↓
    Global Average Pooling 2D
    ↓
    Dense (256 units, ReLU activation)
    ↓
    Batch Normalization
    ↓
    Dropout (0.4)
    ↓
    Dense (4 units, Softmax activation)
    """
    inputs = tf.keras.Input(shape=input_shape, name="mri_input")

    base_model = tf.keras.applications.ResNet50(
        include_top=False,
        weights="imagenet",
        input_tensor=inputs
    )

    if freeze_backbone:
        base_model.trainable = False
    else:
        base_model.trainable = True

    x = base_model.output
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling")(x)
    x = tf.keras.layers.Dense(256, activation="relu", name="dense_feature_head")(x)
    x = tf.keras.layers.BatchNormalization(name="batch_norm")(x)
    x = tf.keras.layers.Dropout(0.4, name="head_dropout")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="classification_output")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="ResNet50_Brain_Tumor_Classifier")

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


if __name__ == "__main__":
    print("Constructing ResNet50 Brain Tumor Classifier...")
    model = build_resnet50_model()
    model.summary()
    print(f"\nModel Name: {model.name}")
    print(f"Total Parameters: {model.count_params():,}")
    trainable_params = sum(tf.keras.backend.count_params(w) for w in model.trainable_weights)
    non_trainable_params = sum(tf.keras.backend.count_params(w) for w in model.non_trainable_weights)
    print(f"Trainable Parameters (Classification Head): {trainable_params:,}")
    print(f"Non-Trainable Parameters (Frozen Backbone): {non_trainable_params:,}")
