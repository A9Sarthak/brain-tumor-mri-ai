"""
Single-image MRI inference module.
Validates input image, applies standardized preprocessing,
computes 4-class softmax probability distribution, and formats output.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
from typing import Dict, Any, Optional
import numpy as np
import tensorflow as tf

from src.config import (
    CLASSES,
    CLASS_DISPLAY_NAMES,
    BEST_MODEL_PATH,
    IMAGE_SIZE,
)
from src.utils import verify_image_file
from src.preprocessing import load_and_preprocess_image


def predict_single_image(
    image_path: str,
    model_or_path: Any = BEST_MODEL_PATH
) -> Dict[str, Any]:
    """
    Perform single-image inference.
    
    Returns:
    {
        "predicted_class": "glioma",
        "predicted_display_name": "Glioma Tumor",
        "confidence_percentage": 98.42,
        "probabilities": {
            "glioma": 0.9842,
            "meningioma": 0.0115,
            "notumor": 0.0025,
            "pituitary": 0.0018
        },
        "probabilities_formatted": {
            "Glioma Tumor": "98.42%",
            ...
        }
    }
    """
    # 1. Model Loading & Verification First
    if isinstance(model_or_path, (str, Path)):
        model_p = Path(model_or_path)
        if not model_p.exists():
            raise FileNotFoundError(f"Model file not found at {model_p}")
        model = tf.keras.models.load_model(model_p)
    elif isinstance(model_or_path, tf.keras.Model):
        model = model_or_path
    else:
        raise TypeError("model_or_path must be a file Path, str, or tf.keras.Model instance.")

    # 2. Image Verification
    img_path = Path(image_path).resolve()
    is_valid, err_msg, dims = verify_image_file(img_path)
    if not is_valid:
        raise ValueError(f"Invalid image file ({img_path.name}): {err_msg}")

    # 3. Preprocessing
    processed_tensor = load_and_preprocess_image(str(img_path), target_size=IMAGE_SIZE)
    batch_tensor = tf.expand_dims(processed_tensor, axis=0)

    # 4. Inference
    raw_preds = model(batch_tensor, training=False).numpy()[0]
    pred_idx = int(np.argmax(raw_preds))
    pred_class = CLASSES[pred_idx]
    confidence_pct = float(raw_preds[pred_idx] * 100.0)

    probs_dict = {cls: float(raw_preds[i]) for i, cls in enumerate(CLASSES)}
    probs_formatted = {
        CLASS_DISPLAY_NAMES[cls]: f"{raw_preds[i] * 100.0:.2f}%"
        for i, cls in enumerate(CLASSES)
    }

    result = {
        "image_path": str(img_path),
        "dimensions": dims,
        "predicted_class": pred_class,
        "predicted_display_name": CLASS_DISPLAY_NAMES[pred_class],
        "confidence_percentage": round(confidence_pct, 2),
        "probabilities": probs_dict,
        "probabilities_formatted": probs_formatted,
        "raw_logits_or_probs": raw_preds.tolist(),
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify a single Brain MRI scan")
    parser.add_argument("--image", type=str, required=True, help="Path to brain MRI image")
    parser.add_argument("--model", type=str, default=str(BEST_MODEL_PATH), help="Path to trained model checkpoint")
    args = parser.parse_args()

    res = predict_single_image(args.image, model_or_path=args.model)

    print("\n" + "=" * 45)
    print("BRAIN TUMOR MRI PREDICTION")
    print("=" * 45)
    print(f"File: {Path(res['image_path']).name}")
    print(f"Image Dimensions: {res['dimensions'][0]} x {res['dimensions'][1]} px")
    print("-" * 45)
    print(f"Prediction: {res['predicted_display_name']} ({res['predicted_class']})")
    print(f"Confidence: {res['confidence_percentage']:.2f}%")
    print("-" * 45)
    print("Probabilities:")
    for display_name, pct_str in res["probabilities_formatted"].items():
        print(f"  {display_name:<20}: {pct_str}")
    print("=" * 45)
