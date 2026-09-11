from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    input_shape: List[Optional[int]]
    num_classes: int
    classes: List[str]

class PredictionResponse(BaseModel):
    analysis_id: str
    prediction: str
    predicted_index: int
    confidence: float
    probabilities: Dict[str, float]
    processing_time_ms: float

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
    analysis_id: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str

class ReportResponse(BaseModel):
    analysis_id: str
    report_text: str
    generated_at: str
