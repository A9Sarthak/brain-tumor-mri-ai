import io
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List

class ImageQualityChecker:
    """
    Independent MRI image quality inspector.
    Inspects technical characteristics of the image without modifying image content.
    """

    @staticmethod
    def inspect(image_bytes: bytes) -> Dict[str, Any]:
        warnings: List[str] = []
        checks = {
            "readable": False,
            "dimensions": False,
            "brightness": False,
            "contrast": False,
            "sharpness": False
        }

        # 1. Check readability and decode
        if not image_bytes or len(image_bytes) == 0:
            return {
                "status": "rejected",
                "score": 0,
                "warnings": ["File payload is empty (0 bytes)."],
                "checks": checks,
                "metrics": {}
            }

        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            # Verify file integrity
            pil_img.verify()
            # Reopen after verify() since verify() alters file pointer
            pil_img = Image.open(io.BytesIO(image_bytes))
            width, height = pil_img.size
            checks["readable"] = True
        except Exception as e:
            return {
                "status": "rejected",
                "score": 0,
                "warnings": ["Corrupted or unreadable image file."],
                "checks": checks,
                "metrics": {}
            }

        # Convert to numpy array for metric inspection (RGB & Grayscale)
        rgb_img = pil_img.convert("RGB")
        arr_rgb = np.array(rgb_img, dtype=np.float32) / 255.0
        
        # Grayscale standard luminance
        gray = 0.2989 * arr_rgb[:, :, 0] + 0.5870 * arr_rgb[:, :, 1] + 0.1140 * arr_rgb[:, :, 2]
        gray_uint8 = (gray * 255.0).astype(np.uint8)

        # 2. Dimensions & Aspect Ratio Check
        min_dim = min(width, height)
        max_dim = max(width, height)
        aspect_ratio = float(width) / float(max(1, height))

        if width < 32 or height < 32:
            return {
                "status": "rejected",
                "score": 0,
                "warnings": [f"Image resolution ({width}x{height}) is too small for clinical evaluation."],
                "checks": checks,
                "metrics": {"width": width, "height": height}
            }

        if aspect_ratio < 0.25 or aspect_ratio > 4.0:
            return {
                "status": "rejected",
                "score": 0,
                "warnings": [f"Extreme aspect ratio ({aspect_ratio:.2f}) indicates an unusable crop or non-scan."],
                "checks": checks,
                "metrics": {"width": width, "height": height, "aspect_ratio": aspect_ratio}
            }

        checks["dimensions"] = True
        if min_dim < 150:
            warnings.append(f"Low resolution ({width}x{height}). Recommended scan resolution is ≥ 224x224.")

        # 3. Brightness & Extreme Clipping
        mean_brightness = float(np.mean(gray))
        pct_almost_black = float(np.mean(gray < (5.0 / 255.0)) * 100.0)
        pct_almost_white = float(np.mean(gray > (250.0 / 255.0)) * 100.0)

        # Check for completely blank/solid images
        if mean_brightness < 0.015:  # essentially all black
            return {
                "status": "rejected",
                "score": 0,
                "warnings": ["Completely black or underexposed image content."],
                "checks": checks,
                "metrics": {"mean_brightness": mean_brightness}
            }

        if mean_brightness > 0.98:  # essentially solid white
            return {
                "status": "rejected",
                "score": 0,
                "warnings": ["Completely white or overexposed image content."],
                "checks": checks,
                "metrics": {"mean_brightness": mean_brightness}
            }

        if mean_brightness < 0.08:
            warnings.append("Low brightness detected; scan appears significantly underexposed.")
        elif mean_brightness > 0.65:
            warnings.append("High overall brightness; scan may have excessive exposure or wash-out.")
        else:
            checks["brightness"] = True

        # 4. Contrast & Dynamic Range
        rms_contrast = float(np.std(gray))
        dynamic_range = float(np.ptp(gray))  # max - min

        if rms_contrast < 0.02 or dynamic_range < 0.08:
            return {
                "status": "rejected",
                "score": 0,
                "warnings": ["Extremely low contrast / uniform image. Insufficient signal dynamic range."],
                "checks": checks,
                "metrics": {"rms_contrast": rms_contrast, "dynamic_range": dynamic_range}
            }

        if rms_contrast < 0.10:
            warnings.append("Low contrast detected. Anatomical contrast between tissue types may be degraded.")
        else:
            checks["contrast"] = True

        # 5. Blur / Sharpness via Variance of Laplacian
        laplacian = cv2.Laplacian(gray_uint8, cv2.CV_64F)
        laplacian_var = float(laplacian.var())

        if laplacian_var < 15.0:
            warnings.append("Low sharpness / blur detected. High-frequency boundary details may be obscured.")
        else:
            checks["sharpness"] = True

        # Compute calibrated quality score (0 - 100)
        score = 100

        # Penalties based on metrics
        if min_dim < 150:
            score -= 15
        elif min_dim < 200:
            score -= 5

        if rms_contrast < 0.12:
            score -= 20
        elif rms_contrast < 0.16:
            score -= 10

        if laplacian_var < 20.0:
            score -= 25
        elif laplacian_var < 50.0:
            score -= 10

        if mean_brightness < 0.10 or mean_brightness > 0.60:
            score -= 15

        if pct_almost_black > 80.0:
            score -= 10
        if pct_almost_white > 30.0:
            score -= 15

        score = max(10, min(100, score))

        # Status determination
        if score >= 75:
            status = "good"
        elif score >= 50:
            status = "fair"
        else:
            status = "poor"

        return {
            "status": status,
            "score": score,
            "warnings": warnings,
            "checks": checks,
            "metrics": {
                "width": width,
                "height": height,
                "aspect_ratio": round(aspect_ratio, 2),
                "mean_brightness": round(mean_brightness, 3),
                "rms_contrast": round(rms_contrast, 3),
                "dynamic_range": round(dynamic_range, 3),
                "sharpness_laplacian_var": round(laplacian_var, 1),
                "pct_almost_black": round(pct_almost_black, 1),
                "pct_almost_white": round(pct_almost_white, 1)
            }
        }
