"""
Modular preprocessing and augmentation pipeline for Brain Tumor MRI images.
"""
from typing import Callable, Tuple
import tensorflow as tf
from src.config import IMAGE_SIZE, INPUT_SHAPE


def get_resnet50_preprocess_fn() -> Callable[[tf.Tensor], tf.Tensor]:
    """Return ResNet50 specific preprocessing function (zero-centered around ImageNet means)."""
    return tf.keras.applications.resnet50.preprocess_input


def get_model_preprocess_fn(architecture_name: str = "ResNet50") -> Callable[[tf.Tensor], tf.Tensor]:
    """Return architecture-specific preprocessing function."""
    arch = architecture_name.lower().replace("-", "").replace("_", "")
    if "efficientnet" in arch:
        return tf.keras.applications.efficientnet.preprocess_input
    elif "mobilenet" in arch:
        return tf.keras.applications.mobilenet_v2.preprocess_input
    elif "vgg" in arch:
        return tf.keras.applications.vgg16.preprocess_input
    else:
        return tf.keras.applications.resnet50.preprocess_input


def build_augmentation_layer() -> tf.keras.Sequential:
    """
    Build data augmentation layer applicable strictly to training images.
    Preserves anatomical plausibility of brain MRI scans.
    """
    return tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.03, fill_mode="nearest"),
        tf.keras.layers.RandomZoom(0.08, fill_mode="nearest"),
        tf.keras.layers.RandomContrast(0.1),
    ], name="mri_augmentation")


def preprocess_image_tensor(
    image_tensor: tf.Tensor,
    target_size: Tuple[int, int] = IMAGE_SIZE,
    preprocess_fn: Callable[[tf.Tensor], tf.Tensor] = None
) -> tf.Tensor:
    """
    Standardize raw RGB image tensor: resize to target resolution and apply model preprocessing.
    """
    if preprocess_fn is None:
        preprocess_fn = get_resnet50_preprocess_fn()
        
    image_tensor = tf.image.resize(image_tensor, target_size)
    # Ensure float32 range before model preprocessing
    image_tensor = tf.cast(image_tensor, tf.float32)
    image_tensor = preprocess_fn(image_tensor)
    return image_tensor


def load_and_preprocess_image(
    image_path: str,
    target_size: Tuple[int, int] = IMAGE_SIZE,
    preprocess_fn: Callable[[tf.Tensor], tf.Tensor] = None
) -> tf.Tensor:
    """
    Load an image from file path and apply standard preprocessing pipeline.
    """
    image_bytes = tf.io.read_file(image_path)
    image = tf.io.decode_image(image_bytes, channels=3, expand_animations=False)
    image.set_shape([None, None, 3])
    return preprocess_image_tensor(image, target_size=target_size, preprocess_fn=preprocess_fn)
