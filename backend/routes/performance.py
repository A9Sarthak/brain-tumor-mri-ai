import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.schemas.analysis import PerformanceResponse
from src.config import METRICS_DIR, LOGS_DIR

router = APIRouter(prefix="/api", tags=["performance"])

@router.get("/performance", response_model=PerformanceResponse)
def get_performance():
    metrics_path = METRICS_DIR / "efficientnet-b0_test_metrics.json"
    history_path = LOGS_DIR / "efficientnet-b0_training_history.json"

    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="Performance metrics artifact not found.")

    with open(metrics_path, "r", encoding="utf-8") as f:
        metrics_data = json.load(f)

    training_history = {}
    if history_path.exists():
        with open(history_path, "r", encoding="utf-8") as f:
            history_data = json.load(f)
            training_history = history_data.get("history", {})

    return PerformanceResponse(
        model_name=metrics_data.get("model_name", "EfficientNet-B0"),
        architecture=metrics_data.get("architecture", "EfficientNet-B0"),
        test_sample_count=metrics_data.get("test_sample_count", 1600),
        accuracy=metrics_data.get("accuracy", 0.80),
        precision_macro=metrics_data.get("precision_macro", 0.8157),
        precision_weighted=metrics_data.get("precision_weighted", 0.8157),
        recall_macro=metrics_data.get("recall_macro", 0.80),
        recall_weighted=metrics_data.get("recall_weighted", 0.80),
        f1_macro=metrics_data.get("f1_macro", 0.7910),
        f1_weighted=metrics_data.get("f1_weighted", 0.7910),
        prediction_distribution=metrics_data.get("prediction_distribution", {}),
        per_class_report=metrics_data.get("per_class_report", {}),
        confusion_matrix_url="/static/confusion_matrices/efficientnet-b0_confusion_matrix.png",
        accuracy_plot_url="/static/plots/efficientnetb0_accuracy.png",
        loss_plot_url="/static/plots/efficientnetb0_loss.png",
        training_history=training_history
    )
