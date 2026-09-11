import io
import base64
from typing import Dict, Tuple
import numpy as np
import tensorflow as tf
from PIL import Image

from src.gradcam import (
    find_target_conv_layer,
    compute_gradcam_heatmap,
    generate_gradcam_overlay,
)

class GradcamService:
    def __init__(self, model):
        self.model = model
        self.target_layer = find_target_conv_layer(model, preferred_name="top_conv")

    def _np_to_base64_png(self, img_array: np.ndarray) -> str:
        pil_img = Image.fromarray(img_array.astype("uint8"))
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64_str}"

    def generate_visualizations(
        self,
        processed_tensor: tf.Tensor,
        orig_np: np.ndarray,
        pred_index: int
    ) -> Dict[str, str]:
        batch_tensor = tf.expand_dims(processed_tensor, axis=0)
        heatmap = compute_gradcam_heatmap(
            self.model,
            batch_tensor,
            target_layer_name=self.target_layer,
            pred_index=pred_index
        )
        
        superimposed_img, colorized_heatmap = generate_gradcam_overlay(
            orig_np,
            heatmap,
            alpha=0.45
        )
        
        return {
            "original_image_base64": self._np_to_base64_png(orig_np),
            "attention_heatmap_base64": self._np_to_base64_png(colorized_heatmap),
            "overlay_image_base64": self._np_to_base64_png(superimposed_img),
            "target_layer": self.target_layer
        }
