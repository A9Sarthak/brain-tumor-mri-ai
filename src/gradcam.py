"""
Grad-CAM (Gradient-weighted Class Activation Mapping) Explainability Engine.
Generates gradient-weighted visual interpretability heatmaps and superimposed MRI overlays
for clinical decision support and transparency.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import Tuple, Dict, Any, Optional, Union
import numpy as np
import tensorflow as tf
import cv2
from PIL import Image

from src.config import IMAGE_SIZE, GRADCAM_TARGET_LAYERS, CLASSES, CLASS_DISPLAY_NAMES
from src.preprocessing import load_and_preprocess_image, get_model_preprocess_fn


def find_target_conv_layer(model: tf.keras.Model, preferred_name: Optional[str] = None) -> str:
    """Find the target convolutional layer in a model."""
    if preferred_name:
        try:
            model.get_layer(preferred_name)
            return preferred_name
        except (ValueError, AttributeError):
            pass

    # Fallback: search backwards for the last 4D output convolutional layer
    for layer in reversed(model.layers):
        try:
            out_shape = layer.output_shape
            if isinstance(out_shape, tuple) and len(out_shape) == 4 and out_shape[1] is not None and out_shape[1] > 1:
                return layer.name
        except Exception:
            continue

    # Secondary fallback: find any Conv2D / Add layer
    for layer in reversed(model.layers):
        name_lower = layer.name.lower()
        if any(term in name_lower for term in ["conv", "out", "add"]):
            return layer.name

    raise ValueError(f"Could not identify a suitable convolutional layer for Grad-CAM in {model.name}.")


def compute_gradcam_heatmap(
    model: tf.keras.Model,
    preprocessed_tensor: tf.Tensor,
    target_layer_name: Optional[str] = None,
    pred_index: Optional[int] = None
) -> np.ndarray:
    """
    Compute Grad-CAM heatmap for a preprocessed input tensor batch (1, H, W, 3).
    Returns a 2D float32 numpy array normalized to [0, 1].
    """
    if target_layer_name is None:
        target_layer_name = find_target_conv_layer(model)

    target_layer = model.get_layer(target_layer_name)

    # Gradient model mapping input to target conv layer output and final prediction
    grad_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=[target_layer.output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(preprocessed_tensor)
        if pred_index is None:
            pred_index = tf.argmax(predictions[0])
        class_channel = predictions[:, pred_index]

    # Compute gradients of class score with respect to feature map activations
    grads = tape.gradient(class_channel, conv_outputs)

    # Global Average Pooling of gradients (neuron importance weights)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    # Weight feature maps by importance weights
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)

    # Apply ReLU: only features with positive influence on the target class
    heatmap = tf.maximum(heatmap, 0.0)

    # Normalize between 0 and 1
    max_val = tf.math.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    else:
        heatmap = tf.zeros_like(heatmap)

    return heatmap.numpy()


def generate_gradcam_overlay(
    original_image: Union[str, Path, np.ndarray, Image.Image],
    heatmap: np.ndarray,
    alpha: float = 0.45,
    colormap: int = cv2.COLORMAP_JET
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate colorized heatmap and superimpose it onto the original MRI scan.
    
    Returns:
    (superimposed_rgb, colorized_heatmap_rgb) as uint8 numpy arrays [0, 255].
    """
    if isinstance(original_image, (str, Path)):
        orig = cv2.imread(str(original_image))
        orig = cv2.cvtColor(orig, cv2.COLOR_BGR2RGB)
    elif isinstance(original_image, Image.Image):
        orig = np.array(original_image.convert("RGB"))
    elif isinstance(original_image, np.ndarray):
        orig = original_image.copy()
        if orig.ndim == 2:
            orig = cv2.cvtColor(orig, cv2.COLOR_GRAY2RGB)
    else:
        raise TypeError("Unsupported original_image type")

    h, w = orig.shape[:2]

    # Resize heatmap to match image dimensions
    resized_heatmap = cv2.resize(heatmap, (w, h))

    # Scale to 8-bit [0, 255]
    heatmap_uint8 = np.uint8(255 * resized_heatmap)

    # Apply colormap
    colorized_bgr = cv2.applyColorMap(heatmap_uint8, colormap)
    colorized_rgb = cv2.cvtColor(colorized_bgr, cv2.COLOR_BGR2RGB)

    # Superimpose: blend original image and colorized heatmap
    superimposed = cv2.addWeighted(orig, 1.0 - alpha, colorized_rgb, alpha, 0)

    return superimposed, colorized_rgb


def analyze_activation_focus(heatmap: np.ndarray) -> Dict[str, Any]:
    """
    Analyze the spatial distribution of the highest Grad-CAM activations.
    Provides diagnostic localization insight for clinical review.
    """
    h, w = heatmap.shape
    y_indices, x_indices = np.where(heatmap >= 0.7 * np.max(heatmap)) if np.max(heatmap) > 0 else ([], [])

    if len(x_indices) == 0:
        peak_y, peak_x = h // 2, w // 2
        coverage_pct = 0.0
    else:
        peak_idx = np.unravel_index(np.argmax(heatmap), heatmap.shape)
        peak_y, peak_x = int(peak_idx[0]), int(peak_idx[1])
        coverage_pct = float(len(x_indices) / (h * w) * 100.0)

    # Relative normalized coordinates
    norm_x = peak_x / w
    norm_y = peak_y / h

    # Determine anatomical region
    if 0.35 <= norm_x <= 0.65 and 0.35 <= norm_y <= 0.70:
        region = "Central / Sellar-Suprasellar Axis (Skull Base)"
    else:
        vert = "Superior (Anterior/Parietal)" if norm_y < 0.5 else "Inferior (Posterior/Occipital)"
        horiz = "Right Hemisphere" if norm_x < 0.5 else "Left Hemisphere"
        region = f"{vert} {horiz}"

    intensity = float(np.max(heatmap)) * 100.0

    return {
        "peak_x": peak_x,
        "peak_y": peak_y,
        "norm_x": round(norm_x, 3),
        "norm_y": round(norm_y, 3),
        "anatomical_region": region,
        "focus_intensity_pct": round(intensity, 2),
        "hotspot_coverage_pct": round(coverage_pct, 2),
    }


def explain_image_prediction(
    image_path: Union[str, Path],
    model: tf.keras.Model,
    architecture_name: str = "ResNet50",
    alpha: float = 0.45
) -> Dict[str, Any]:
    """
    Full Grad-CAM explainability pipeline for a single MRI image.
    
    Returns:
    - predicted_class
    - confidence
    - original_image_rgb
    - superimposed_rgb
    - heatmap_rgb
    - localization_insight
    """
    img_path = Path(image_path).resolve()
    target_layer = GRADCAM_TARGET_LAYERS.get(architecture_name, None)
    if target_layer is None:
        target_layer = find_target_conv_layer(model)

    preprocess_fn = get_model_preprocess_fn(architecture_name)
    processed_tensor = load_and_preprocess_image(str(img_path), target_size=IMAGE_SIZE, preprocess_fn=preprocess_fn)
    batch_tensor = tf.expand_dims(processed_tensor, axis=0)

    # Run inference
    preds = model(batch_tensor, training=False).numpy()[0]
    pred_idx = int(np.argmax(preds))
    pred_class = CLASSES[pred_idx]
    confidence = float(preds[pred_idx] * 100.0)

    # Compute Grad-CAM
    heatmap = compute_gradcam_heatmap(model, batch_tensor, target_layer_name=target_layer, pred_index=pred_idx)

    # Original image for blending
    orig_pil = Image.open(str(img_path)).convert("RGB")
    orig_np = np.array(orig_pil)

    superimposed_rgb, heatmap_rgb = generate_gradcam_overlay(orig_np, heatmap, alpha=alpha)
    localization = analyze_activation_focus(heatmap)

    return {
        "predicted_class": pred_class,
        "predicted_display_name": CLASS_DISPLAY_NAMES[pred_class],
        "confidence_percentage": round(confidence, 2),
        "original_image": orig_np,
        "superimposed_image": superimposed_rgb,
        "heatmap_image": heatmap_rgb,
        "raw_heatmap": heatmap,
        "target_layer_used": target_layer,
        "localization": localization,
    }


if __name__ == "__main__":
    print("Grad-CAM Module initialized successfully.")
