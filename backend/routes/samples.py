from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from backend.schemas.analysis import SampleItem
from src.config import RAW_DATA_DIR

router = APIRouter(prefix="/api", tags=["samples"])

SAMPLE_DEFINITIONS = [
    {
        "id": "notumor",
        "class_name": "notumor",
        "display_name": "No Tumor",
        "filename": "Te-no_1.jpg",
        "src_path": RAW_DATA_DIR / "Testing" / "notumor" / "Te-no_1.jpg",
    },
    {
        "id": "glioma",
        "class_name": "glioma",
        "display_name": "Glioma Tumor",
        "filename": "Te-gl_1.jpg",
        "src_path": RAW_DATA_DIR / "Testing" / "glioma" / "Te-gl_1.jpg",
    },
    {
        "id": "meningioma",
        "class_name": "meningioma",
        "display_name": "Meningioma Tumor",
        "filename": "Te-me_1.jpg",
        "src_path": RAW_DATA_DIR / "Testing" / "meningioma" / "Te-me_1.jpg",
    },
    {
        "id": "pituitary",
        "class_name": "pituitary",
        "display_name": "Pituitary Tumor",
        "filename": "Te-pi_1.jpg",
        "src_path": RAW_DATA_DIR / "Testing" / "pituitary" / "Te-pi_1.jpg",
    },
]

@router.get("/samples", response_model=List[SampleItem])
def get_sample_mris():
    return [
        SampleItem(
            id=item["id"],
            class_name=item["class_name"],
            display_name=item["display_name"],
            filename=item["filename"],
            image_url=f"/api/samples/{item['id']}/image"
        )
        for item in SAMPLE_DEFINITIONS
    ]

@router.get("/samples/{sample_id}/image")
def get_sample_image(sample_id: str):
    matched = next((s for s in SAMPLE_DEFINITIONS if s["id"] == sample_id.lower()), None)
    if not matched:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_id}' not found")
    
    file_path = matched["src_path"]
    if not file_path.exists():
        # Fallback to static folder
        static_path = Path(__file__).resolve().parent.parent / "static" / "samples" / matched["filename"]
        if static_path.exists():
            file_path = static_path
        else:
            raise HTTPException(status_code=404, detail=f"Sample file {matched['filename']} not found on disk")
    
    return FileResponse(str(file_path), media_type="image/jpeg")

