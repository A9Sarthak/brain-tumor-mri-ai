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


def _attach_classification_head(
    base_output: tf.Tensor,
    num_classes: int = NUM_CLASSES
) -> tf.Tensor:
    """Attach standardized classification head with regularization across all backbones."""
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling")(base_output)
    x = tf.keras.layers.Dense(256, activation="relu", name="dense_feature_head")(x)
    x = tf.keras.layers.BatchNormalization(name="batch_norm")(x)
    x = tf.keras.layers.Dropout(0.4, name="head_dropout")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="classification_output")(x)
    return outputs


def build_resnet50_model(
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """Build ResNet50 transfer learning classifier."""
    inputs = tf.keras.Input(shape=input_shape, name="mri_input")
    base_model = tf.keras.applications.ResNet50(include_top=False, weights="imagenet", input_tensor=inputs)
    base_model.trainable = not freeze_backbone
    outputs = _attach_classification_head(base_model.output, num_classes=num_classes)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="ResNet50_Brain_Tumor_Classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def build_efficientnet_model(
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """Build EfficientNet-B0 transfer learning classifier."""
    inputs = tf.keras.Input(shape=input_shape, name="mri_input")
    base_model = tf.keras.applications.EfficientNetB0(include_top=False, weights="imagenet", input_tensor=inputs)
    for layer in base_model.layers:
        layer.trainable = not freeze_backbone
    outputs = _attach_classification_head(base_model.output, num_classes=num_classes)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="EfficientNetB0_Brain_Tumor_Classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def build_mobilenet_model(
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """Build MobileNetV2 transfer learning classifier."""
    inputs = tf.keras.Input(shape=input_shape, name="mri_input")
    base_model = tf.keras.applications.MobileNetV2(include_top=False, weights="imagenet", input_tensor=inputs)
    base_model.trainable = not freeze_backbone
    outputs = _attach_classification_head(base_model.output, num_classes=num_classes)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="MobileNetV2_Brain_Tumor_Classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def build_vgg16_model(
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """Build VGG16 transfer learning classifier."""
    inputs = tf.keras.Input(shape=input_shape, name="mri_input")
    base_model = tf.keras.applications.VGG16(include_top=False, weights="imagenet", input_tensor=inputs)
    base_model.trainable = not freeze_backbone
    outputs = _attach_classification_head(base_model.output, num_classes=num_classes)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="VGG16_Brain_Tumor_Classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def build_model(
    architecture_name: str = "ResNet50",
    input_shape: Tuple[int, int, int] = INPUT_SHAPE,
    num_classes: int = NUM_CLASSES,
    freeze_backbone: bool = True,
    learning_rate: float = LEARNING_RATE
) -> tf.keras.Model:
    """Factory dispatcher for building any of the 4 Phase 2 architectures."""
    arch = architecture_name.lower().replace("-", "").replace("_", "")
    if "efficientnet" in arch:
        return build_efficientnet_model(input_shape, num_classes, freeze_backbone, learning_rate)
    elif "mobilenet" in arch:
        return build_mobilenet_model(input_shape, num_classes, freeze_backbone, learning_rate)
    elif "vgg" in arch:
        return build_vgg16_model(input_shape, num_classes, freeze_backbone, learning_rate)
    elif "resnet" in arch:
        return build_resnet50_model(input_shape, num_classes, freeze_backbone, learning_rate)
    else:
        raise ValueError(f"Unknown architecture: {architecture_name}. Choose from ResNet50, EfficientNet-B0, MobileNetV2, VGG16.")


if __name__ == "__main__":
    print("Constructing 4 Transfer Learning Classifiers...")
    for arch in ["ResNet50", "EfficientNet-B0", "MobileNetV2", "VGG16"]:
        m = build_model(arch)
        print(f"[{arch}] Model: {m.name} | Total Params: {m.count_params():,}")
