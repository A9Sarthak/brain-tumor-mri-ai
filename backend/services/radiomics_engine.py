"""
Quantitative Radiomics & Morphometry Engine for NeuroScan AI.
Transforms 2D Grad-CAM saliency activations into quantified neuro-oncological biomarkers,
including cross-sectional area, sphericity index, margin irregularity, and anatomical compartment mapping.
"""
import io
import base64
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
import cv2
from PIL import Image

class RadiomicsEngine:
    """
    Extracts morphometric and spatial biomarkers from MRI scans and attention maps.
    Standardized to typical adult cranial MRI FOV (220mm x 220mm) mapped to 224x224 pixels.
    Pixel spacing: ~0.982 mm/pixel -> 1 px^2 approx 0.965 mm^2.
    """
    MM2_PER_PIXEL = 0.965
    MM_PER_PIXEL = 0.982

    @classmethod
    def extract_biomarkers(
        cls,
        orig_np: np.ndarray,
        heatmap: np.ndarray,
        predicted_class: str,
        confidence: float
    ) -> Dict[str, Any]:
        """
        Extracts radiomic shape features, surface area, and anatomical compartment.
        """
        h, w = orig_np.shape[:2]

        # Ensure heatmap matches original image dimensions
        if heatmap.shape[:2] != (h, w):
            heatmap = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_LINEAR)

        # Handle 'No Tumor' case
        if predicted_class == "No Tumor":
            return {
                "lesion_detected": False,
                "estimated_area_mm2": 0.0,
                "estimated_area_pixels": 0,
                "slice_occupancy_pct": 0.0,
                "perimeter_mm": 0.0,
                "sphericity_index": 1.0,
                "margin_irregularity": 0.0,
                "aspect_ratio": 1.0,
                "anatomical_locus": "Normal Cranial Parenchyma (Bilateral Hemispheric Symmetry)",
                "morphology_summary": "No focal pathological mass detected. Parenchymal architecture and ventricular symmetry are intact.",
                "contour_overlay_base64": None,
                "contour_coordinates": [],
                "bounding_box": None,
            }

        # 1. Adaptive Otsu Thresholding on Smoothed Heatmap
        # Heatmap is float in [0.0, 1.0]
        heat_uint8 = np.clip(heatmap * 255.0, 0, 255).astype(np.uint8)
        blurred_heat = cv2.GaussianBlur(heat_uint8, (9, 9), 0)

        # Use Otsu's method with a safe floor of 85 (approx 0.33 activation)
        otsu_val, _ = cv2.threshold(blurred_heat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        threshold_val = max(int(otsu_val), 85)
        _, binary_mask = cv2.threshold(blurred_heat, threshold_val, 255, cv2.THRESH_BINARY)

        # Morphological opening and closing to clean spurious noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        cleaned_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel, iterations=1)

        # 2. Extract Connected Contours
        contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            # Fallback if threshold was too aggressive: pick top 20% percentile
            p80 = np.percentile(heat_uint8, 80)
            _, binary_mask = cv2.threshold(heat_uint8, int(p80), 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return {
                "lesion_detected": False,
                "estimated_area_mm2": 0.0,
                "estimated_area_pixels": 0,
                "slice_occupancy_pct": 0.0,
                "perimeter_mm": 0.0,
                "sphericity_index": 0.0,
                "margin_irregularity": 0.0,
                "aspect_ratio": 1.0,
                "anatomical_locus": "Diffuse / Indeterminate Activation",
                "morphology_summary": "Diffuse signal without a discrete segmentable margin.",
                "contour_overlay_base64": None,
                "contour_coordinates": [],
                "bounding_box": None,
            }

        # Select dominant contour by area
        primary_contour = max(contours, key=cv2.contourArea)
        area_px = float(cv2.contourArea(primary_contour))
        total_slice_area = float(h * w)
        occupancy_pct = round((area_px / total_slice_area) * 100.0, 2)
        area_mm2 = round(area_px * cls.MM2_PER_PIXEL, 1)

        # Perimeter
        perimeter_px = float(cv2.arcLength(primary_contour, True))
        perimeter_mm = round(perimeter_px * cls.MM_PER_PIXEL, 1)

        # Sphericity / Circularity: Psi = (4 * pi * Area) / (Perimeter^2)
        if perimeter_px > 0:
            sphericity = float((4.0 * np.pi * area_px) / (perimeter_px ** 2))
            sphericity = round(min(1.0, max(0.05, sphericity)), 3)
        else:
            sphericity = 0.50

        # Margin Irregularity via Convex Hull Solidity
        hull = cv2.convexHull(primary_contour)
        hull_area = float(cv2.contourArea(hull))
        solidity = float(area_px / (hull_area + 1e-6))
        margin_irregularity = round(min(1.0, max(0.0, 1.0 - solidity)), 3)

        # Aspect Ratio via Bounding Rect or Fitted Ellipse
        bx, by, bw, bh = cv2.boundingRect(primary_contour)
        if len(primary_contour) >= 5:
            try:
                ellipse = cv2.fitEllipse(primary_contour)
                (cx_e, cy_e), (ma, MA), angle = ellipse
                major_axis = max(ma, MA)
                minor_axis = min(ma, MA)
                aspect_ratio = round(float(major_axis / (minor_axis + 1e-6)), 2)
            except Exception:
                aspect_ratio = round(float(max(bw, bh) / (min(bw, bh) + 1e-6)), 2)
        else:
            aspect_ratio = round(float(max(bw, bh) / (min(bw, bh) + 1e-6)), 2)

        # Moments & Centroid
        M = cv2.moments(primary_contour)
        if M["m00"] > 0:
            cx = float(M["m10"] / M["m00"])
            cy = float(M["m01"] / M["m00"])
        else:
            cx, cy = float(bx + bw / 2), float(by + bh / 2)

        norm_cx = cx / float(w)
        norm_cy = cy / float(h)

        # 3. Anatomical Compartment Classification Heuristic
        # Sellar region: cy in [0.52, 0.76], cx in [0.40, 0.60] (central skull base)
        if 0.40 <= norm_cx <= 0.60 and 0.50 <= norm_cy <= 0.78 and "pituitary" in predicted_class.lower():
            anatomical_locus = "Sellar / Pituitary Fossa (Hypophyseal Axis)"
            morphology_summary = (
                f"Circumscribed sellar/suprasellar mass ({area_mm2} mm²). "
                f"Sphericity index: {sphericity:.2f} with smooth borders, characteristic of adenoma."
            )
        elif 0.38 <= norm_cx <= 0.62 and 0.52 <= norm_cy <= 0.76:
            anatomical_locus = "Sellar / Suprasellar Skull Base"
            morphology_summary = (
                f"Skull-base focal lesion ({area_mm2} mm²) with localized mass effect."
            )
        else:
            # Check proximity to outer skull vault
            dist_from_center = np.sqrt((norm_cx - 0.5) ** 2 + (norm_cy - 0.5) ** 2)
            if dist_from_center > 0.28:
                anatomical_locus = "Extra-Axial Convexity / Parasagittal Dural Attachment"
                if sphericity >= 0.65:
                    morphology_summary = (
                        f"Well-circumscribed extra-axial lesion ({area_mm2} mm²) with high sphericity ({sphericity:.2f}), "
                        "typical of dural-based meningioma."
                    )
                else:
                    morphology_summary = (
                        f"Extra-axial lesion ({area_mm2} mm²) displaying localized dural abutment."
                    )
            else:
                anatomical_locus = "Intra-Axial Cerebral Hemispheric (Deep White Matter)"
                if margin_irregularity >= 0.18 or sphericity < 0.60:
                    morphology_summary = (
                        f"Infiltrative intra-axial lesion ({area_mm2} mm²) with irregular margins "
                        f"(irregularity: {margin_irregularity:.2f}), typical of glial neoplasms."
                    )
                else:
                    morphology_summary = (
                        f"Intra-axial focal parenchymal lesion ({area_mm2} mm²)."
                    )

        # 4. Generate Precision Contour Overlay Visualization
        overlay_canvas = orig_np.copy()
        if overlay_canvas.ndim == 2:
            overlay_canvas = cv2.cvtColor(overlay_canvas, cv2.COLOR_GRAY2RGB)
        elif overlay_canvas.shape[2] == 4:
            overlay_canvas = cv2.cvtColor(overlay_canvas, cv2.COLOR_RGBA2RGB)

        # Draw contour line with bright cyan color
        cv2.drawContours(overlay_canvas, [primary_contour], -1, (6, 182, 212), 2)  # Cyan #06b6d4

        # Draw subtle bounding box with corner markers
        cv2.rectangle(overlay_canvas, (bx, by), (bx + bw, by + bh), (14, 165, 233), 1)
        corner_len = min(12, min(bw, bh) // 3)
        cv2.line(overlay_canvas, (bx, by), (bx + corner_len, by), (6, 182, 212), 2)
        cv2.line(overlay_canvas, (bx, by), (bx, by + corner_len), (6, 182, 212), 2)
        cv2.line(overlay_canvas, (bx + bw, by + bh), (bx + bw - corner_len, by + bh), (6, 182, 212), 2)
        cv2.line(overlay_canvas, (bx + bw, by + bh), (bx + bw - corner_len, by + bh), (6, 182, 212), 2)

        # Centroid dot
        cv2.circle(overlay_canvas, (int(cx), int(cy)), 3, (244, 63, 94), -1)  # Rose dot

        # Convert overlay to Base64 PNG
        pil_img = Image.fromarray(overlay_canvas.astype("uint8"))
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        overlay_b64 = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

        # Sample contour points for lightweight vector rendering if needed
        approx_contour = cv2.approxPolyDP(primary_contour, epsilon=1.5, closed=True)
        pts_list = [[int(pt[0][0]), int(pt[0][1])] for pt in approx_contour]

        return {
            "lesion_detected": True,
            "estimated_area_mm2": area_mm2,
            "estimated_area_pixels": int(area_px),
            "slice_occupancy_pct": occupancy_pct,
            "perimeter_mm": perimeter_mm,
            "sphericity_index": sphericity,
            "margin_irregularity": margin_irregularity,
            "aspect_ratio": aspect_ratio,
            "anatomical_locus": anatomical_locus,
            "morphology_summary": morphology_summary,
            "contour_overlay_base64": overlay_b64,
            "contour_coordinates": pts_list[:60],
            "bounding_box": {"x": int(bx), "y": int(by), "width": int(bw), "height": int(bh)},
            "centroid": {"x": round(cx, 1), "y": round(cy, 1)},
            "binary_mask": cleaned_mask,
        }
