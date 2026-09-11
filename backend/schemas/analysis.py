from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    input_shape: List[Optional[int]]
    num_classes: int
    classes: List[str]

class QualityChecks(BaseModel):
    readable: bool
    dimensions: bool
    brightness: bool
    contrast: bool
    sharpness: bool

class QualityResult(BaseModel):
    status: str  # good, fair, poor, rejected
    score: int
    warnings: List[str]
    checks: QualityChecks
    metrics: Optional[Dict[str, Any]] = None

class OODResult(BaseModel):
    status: str  # in_distribution, uncertain, out_of_distribution
    score: float
    warning: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class ValidationResult(BaseModel):
    quality: QualityResult
    ood: OODResult
    is_acceptable: bool
    action: str  # proceed, withhold, reject
    reason: Optional[str] = None

class PredictionResponse(BaseModel):
    analysis_id: str
    prediction: str
    predicted_index: int
    confidence: float
    probabilities: Dict[str, float]
    processing_time_ms: float
    validation: Optional[ValidationResult] = None
    is_withheld: bool = False
    withheld_reason: Optional[str] = None

class GradcamResponse(BaseModel):
    analysis_id: str
    prediction: str
    original_image_base64: str
    attention_heatmap_base64: str
    overlay_image_base64: str
    target_layer: str

class MetricDetail(BaseModel):
    precision: float
    recall: float
    f1_score: float = Field(alias="f1-score")
    support: float

class PerformanceResponse(BaseModel):
    model_name: str
    architecture: str
    test_sample_count: int
    accuracy: float
    precision_macro: float
    precision_weighted: float
    recall_macro: float
    recall_weighted: float
    f1_macro: float
    f1_weighted: float
    prediction_distribution: Dict[str, int]
    per_class_report: Dict[str, Any]
    confusion_matrix_url: str
    accuracy_plot_url: str
    loss_plot_url: str
    training_history: Dict[str, Any]

class SampleItem(BaseModel):
    id: str
    class_name: str
    display_name: str
    filename: str
    image_url: str

class ReportRequest(BaseModel):
    analysis_id: Optional[str] = None
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: Optional[str] = None
    validation: Optional[ValidationResult] = None
    is_withheld: Optional[bool] = False
    withheld_reason: Optional[str] = None
    image_filename: Optional[str] = None
    clinical_notes: Optional[str] = None

class ReportResponse(BaseModel):
    analysis_id: str
    report_text: str
    generated_at: str
