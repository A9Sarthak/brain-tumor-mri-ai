from typing import Dict, Any, Optional
from backend.services.image_quality import ImageQualityChecker
from backend.services.ood_detector import OODDetector

class InputValidationService:
    """
    Validation gatekeeper coordinating Image Quality Check and OOD Detection.
    """

    @staticmethod
    def validate_input(image_bytes: bytes, prediction_probabilities: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        quality = ImageQualityChecker.inspect(image_bytes)
        
        # If rejected at the quality level (e.g. unreadable/blank), OOD is immediately out_of_distribution
        if quality["status"] == "rejected":
            ood = {
                "status": "out_of_distribution",
                "score": 1.0,
                "warning": "Input failed basic image quality checks and cannot be processed as a valid MRI scan."
            }
            return {
                "quality": quality,
                "ood": ood,
                "is_acceptable": False,
                "action": "reject",
                "reason": quality["warnings"][0] if quality["warnings"] else "Image rejected by quality inspection."
            }

        # Run OOD detection
        ood = OODDetector.evaluate(image_bytes, prediction_probabilities=prediction_probabilities)

        if ood["status"] == "out_of_distribution":
            return {
                "quality": quality,
                "ood": ood,
                "is_acceptable": False,
                "action": "withhold",
                "reason": ood["warning"]
            }

        return {
            "quality": quality,
            "ood": ood,
            "is_acceptable": True,
            "action": "proceed",
            "reason": None
        }
