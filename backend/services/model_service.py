import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import io
import time
from typing import Dict, Any, Tuple
import numpy as np
import tensorflow as tf
from PIL import Image

from src.config import (
    MODELS_DIR,
    CLASSES,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE,
    CLASS_NAMES_LIST,
)
from src.preprocessing import get_model_preprocess_fn, preprocess_image_tensor

class ModelService:
    _instance = None

    def __init__(self):
        self.model = None
        self.preprocess_fn = None
        self.model_path = None
        self.input_shape = None
        self.num_classes = len(CLASSES)
        self.classes = [CLASS_DISPLAY_NAMES[c] for c in CLASSES]
        self._load_model()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_model(self):
        primary_path = MODELS_DIR / "best_efficientnet_model.keras"
        fallback_path = MODELS_DIR / "efficientnetb0_best.keras"
        
        if primary_path.exists():
            self.model_path = primary_path
        elif fallback_path.exists():
            self.model_path = fallback_path
        else:
            raise FileNotFoundError(f"No trained model found at {primary_path} or {fallback_path}")

        print(f"[ModelService] Loading model from {self.model_path}...")
        self.model = tf.keras.models.load_model(self.model_path)
        self.preprocess_fn = get_model_preprocess_fn("EfficientNet-B0")
        self.input_shape = list(self.model.input_shape)
        assert self.model.output_shape[-1] == 4, f"Model must output 4 classes, got {self.model.output_shape[-1]}"
        print(f"[ModelService] Successfully loaded {self.model.name} with input {self.input_shape} and 4 classes.")

    def preprocess_image_bytes(self, image_bytes: bytes) -> Tuple[tf.Tensor, np.ndarray]:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_np = np.array(pil_img)
        
        img_tensor = tf.convert_to_tensor(orig_np, dtype=tf.uint8)
        processed_tensor = preprocess_image_tensor(
            img_tensor,
            target_size=IMAGE_SIZE,
            preprocess_fn=self.preprocess_fn
        )
        return processed_tensor, orig_np

    def predict(self, processed_tensor: tf.Tensor) -> Dict[str, Any]:
        start_time = time.time()
        batch_tensor = tf.expand_dims(processed_tensor, axis=0)
        preds = self.model(batch_tensor, training=False).numpy()[0]
        
        pred_idx = int(np.argmax(preds))
        pred_class_code = CLASSES[pred_idx]
        display_name = CLASS_DISPLAY_NAMES[pred_class_code]
        confidence = float(preds[pred_idx])
        
        probabilities = {
            CLASS_DISPLAY_NAMES[c]: float(preds[i])
            for i, c in enumerate(CLASSES)
        }
        
        duration_ms = (time.time() - start_time) * 1000.0
        
        return {
            "prediction": display_name,
            "predicted_index": pred_idx,
            "confidence": confidence,
            "probabilities": probabilities,
            "processing_time_ms": round(duration_ms, 2)
        }
