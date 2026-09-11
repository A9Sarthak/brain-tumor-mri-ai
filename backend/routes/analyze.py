import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.schemas.analysis import PredictionResponse, GradcamResponse
from backend.services.model_service import ModelService
from backend.services.gradcam_service import GradcamService
from backend.routes.samples import resolve_sample_file

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
        if len(contents) == 0:
            if sample_class:
                sample_path = resolve_sample_file(sample_class)
                with open(sample_path, "rb") as f:
                    contents = f.read()
            elif any(s in (file.filename or "").lower() for s in ["te-no", "te-gl", "te-me", "te-pi", "glioma", "meningioma", "pituitary", "notumor"]):
                # Detect matching sample from filename
                matched_id = "notumor" if "no" in file.filename.lower() else "glioma" if "gl" in file.filename.lower() else "meningioma" if "me" in file.filename.lower() else "pituitary"
                sample_path = resolve_sample_file(matched_id)
                with open(sample_path, "rb") as f:
                    contents = f.read()
            else:
                raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes). Please select a valid MRI image scan.")

        if len(contents) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail="File exceeds maximum allowed size of 200MB.")
    else:
        # Load sample from disk using verified sample repository
        sample_path = resolve_sample_file(sample_class)
        with open(sample_path, "rb") as f:
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
        if len(contents) == 0:
            if sample_class:
                sample_path = resolve_sample_file(sample_class)
                with open(sample_path, "rb") as f:
                    contents = f.read()
            elif any(s in (file.filename or "").lower() for s in ["te-no", "te-gl", "te-me", "te-pi", "glioma", "meningioma", "pituitary", "notumor"]):
                matched_id = "notumor" if "no" in file.filename.lower() else "glioma" if "gl" in file.filename.lower() else "meningioma" if "me" in file.filename.lower() else "pituitary"
                sample_path = resolve_sample_file(matched_id)
                with open(sample_path, "rb") as f:
                    contents = f.read()
            else:
                raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes). Please select a valid MRI image scan.")
    else:
        sample_path = resolve_sample_file(sample_class)
        with open(sample_path, "rb") as f:
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
