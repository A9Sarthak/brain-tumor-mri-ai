import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.schemas.analysis import PredictionResponse, GradcamResponse
from backend.services.model_service import ModelService
from backend.services.gradcam_service import GradcamService

router = APIRouter(prefix="/api", tags=["analyze"])

VALID_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB

@router.post("/analyze", response_model=PredictionResponse)
async def analyze_mri(
    file: Optional[UploadFile] = File(None),
    sample_class: Optional[str] = Form(None)
):
    model_service = ModelService.get_instance()

    if file is None and sample_class is None:
        raise HTTPException(status_code=400, detail="Either an MRI image file or sample_class must be provided.")

    if file:
        filename = file.filename or "upload.jpg"
        ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
        if ext not in VALID_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported format '{ext}'. Only JPG, JPEG, and PNG are allowed.")
        
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 200MB.")
    else:
        # Load sample from disk
        from src.config import TEST_MANIFEST
        import pandas as pd
        df = pd.read_csv(TEST_MANIFEST)
        sample_rows = df[df["class_name"] == sample_class.lower()]
        if sample_rows.empty:
            raise HTTPException(status_code=404, detail=f"Sample for class '{sample_class}' not found.")
        filepath = sample_rows.iloc[0]["filepath"]
        with open(filepath, "rb") as f:
            contents = f.read()

    try:
        processed_tensor, _ = model_service.preprocess_image_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image content: Unable to decode MRI scan.")

    result = model_service.predict(processed_tensor)
    analysis_id = str(uuid.uuid4())

    return PredictionResponse(
        analysis_id=analysis_id,
        prediction=result["prediction"],
        predicted_index=result["predicted_index"],
        confidence=result["confidence"],
        probabilities=result["probabilities"],
        processing_time_ms=result["processing_time_ms"]
    )

@router.post("/gradcam", response_model=GradcamResponse)
async def generate_gradcam(
    file: Optional[UploadFile] = File(None),
    sample_class: Optional[str] = Form(None)
):
    model_service = ModelService.get_instance()
    gradcam_service = GradcamService(model_service.model)

    if file is None and sample_class is None:
        raise HTTPException(status_code=400, detail="Either an MRI image file or sample_class must be provided.")

    if file:
        contents = await file.read()
    else:
        from src.config import TEST_MANIFEST
        import pandas as pd
        df = pd.read_csv(TEST_MANIFEST)
        sample_rows = df[df["class_name"] == sample_class.lower()]
        if sample_rows.empty:
            raise HTTPException(status_code=404, detail=f"Sample for class '{sample_class}' not found.")
        filepath = sample_rows.iloc[0]["filepath"]
        with open(filepath, "rb") as f:
            contents = f.read()

    try:
        processed_tensor, orig_np = model_service.preprocess_image_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Unable to decode MRI scan.")

    result = model_service.predict(processed_tensor)
    pred_idx = result["predicted_index"]
    
    vis = gradcam_service.generate_visualizations(
        processed_tensor=processed_tensor,
        orig_np=orig_np,
        pred_index=pred_idx
    )

    return GradcamResponse(
        analysis_id=str(uuid.uuid4()),
        prediction=result["prediction"],
        original_image_base64=vis["original_image_base64"],
        attention_heatmap_base64=vis["attention_heatmap_base64"],
        overlay_image_base64=vis["overlay_image_base64"],
        target_layer=vis["target_layer"]
    )
