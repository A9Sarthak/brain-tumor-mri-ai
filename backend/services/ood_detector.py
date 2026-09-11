import io
import numpy as np
from PIL import Image
from typing import Dict, Any, Optional

class OODDetector:
    """
    Independent Out-of-Distribution (OOD) Detector.
    Determines whether an uploaded image conforms to the axial brain MRI distribution
    without modifying or retraining the existing EfficientNet-B0 model.
    """

    @staticmethod
    def evaluate(image_bytes: bytes, prediction_probabilities: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Evaluates domain consistency and returns status, OOD anomaly score (0.0 to 1.0), and warning.
        """
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((224, 224))
            arr = np.array(pil_img, dtype=np.float32) / 255.0
        except Exception:
            return {
                "status": "out_of_distribution",
                "score": 1.0,
                "warning": "Input could not be processed as an image scan."
            }

        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

        # 1. Color Divergence (MRIs are monochromatic/grayscale)
        rg_diff = np.mean(np.abs(r - g))
        rb_diff = np.mean(np.abs(r - b))
        color_diff = float((rg_diff + rb_diff) / 2.0)

        # 2. Background Ratio (Air surrounding the skull)
        bg_ratio = float(np.mean(gray < 0.08))

        # 3. Document / Bright White Ratio
        white_ratio = float(np.mean(gray > 0.85))

        # 4. Central Brain Mass vs Border Air Ratio
        h, w = gray.shape
        border_mask = np.ones((h, w), dtype=bool)
        border_mask[int(h * 0.2):int(h * 0.8), int(w * 0.2):int(w * 0.8)] = False
        border_mean = float(np.mean(gray[border_mask]))
        center_mean = float(np.mean(gray[~border_mask]))
        center_to_border_ratio = float((center_mean + 1e-4) / (border_mean + 1e-4))

        # Anomaly score calculation
        anomaly_points = 0.0

        # Check A: Color photographic content
        if color_diff > 0.08:
            anomaly_points += 0.85  # Strong indication of natural color photo/graphic
        elif color_diff > 0.035:
            anomaly_points += 0.45

        # Check B: Document, slide, or screenshot (high white content)
        if white_ratio > 0.35:
            anomaly_points += 0.85
        elif white_ratio > 0.20:
            anomaly_points += 0.40

        # Check C: Complete lack of skull/air background boundary (e.g. landscape, textured photo)
        if bg_ratio < 0.05:
            anomaly_points += 0.45
        elif bg_ratio < 0.10:
            anomaly_points += 0.20

        # Check D: Centrally focused anatomical mass vs borders
        # Brain MRIs have bright tissue in center, dark air on borders (ratio >= 1.25).
        # Inverted or flat contrast (ratio < 1.05) indicates document or inverted non-scan.
        if center_to_border_ratio < 1.05:
            anomaly_points += 0.45
        elif center_to_border_ratio < 1.20 and bg_ratio < 0.20:
            anomaly_points += 0.25

        # Check E: Softmax entropy / confidence if available
        if prediction_probabilities:
            probs = np.array(list(prediction_probabilities.values()), dtype=np.float32)
            max_p = float(np.max(probs))
            entropy = float(-np.sum(probs * np.log(probs + 1e-12)))
            # Max possible entropy for 4 classes is ln(4) ~= 1.386
            if max_p < 0.35 or entropy > 1.30:
                anomaly_points += 0.25

        # Clamp OOD score to [0.0, 1.0]
        ood_score = round(min(1.0, max(0.0, anomaly_points)), 2)

        if ood_score >= 0.65:
            status = "out_of_distribution"
            warning = "This image appears substantially different from the MRI data used by this model. A reliable classification cannot be provided."
        elif ood_score >= 0.35:
            status = "uncertain"
            warning = "Input exhibits borderline distribution characteristics. Review scan provenance before clinical interpretation."
        else:
            status = "in_distribution"
            warning = None

        return {
            "status": status,
            "score": ood_score,
            "warning": warning,
            "metrics": {
                "color_diff": round(color_diff, 4),
                "bg_ratio": round(bg_ratio, 3),
                "white_ratio": round(white_ratio, 3),
                "center_to_border_ratio": round(center_to_border_ratio, 2)
            }
        }
