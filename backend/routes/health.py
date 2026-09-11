from fastapi import APIRouter
from backend.schemas.analysis import HealthResponse
from backend.services.model_service import ModelService

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health", response_model=HealthResponse)
def get_health():
    model_service = ModelService.get_instance()
    return HealthResponse(
        status="healthy",
        model_loaded=model_service.model is not None,
        model_name=model_service.model.name if model_service.model else "unknown",
        input_shape=model_service.input_shape or [],
        num_classes=model_service.num_classes,
        classes=model_service.classes
    )
