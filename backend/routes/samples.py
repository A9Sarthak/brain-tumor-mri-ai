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
        "filename": "Te-me_11.jpg",
        "src_path": RAW_DATA_DIR / "Testing" / "meningioma" / "Te-me_11.jpg",
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

def resolve_sample_file(identifier: str) -> Path:
    ident = identifier.lower().replace(" ", "").replace("_", "").replace("-", "")
    for s in SAMPLE_DEFINITIONS:
        s_id = s["id"].lower().replace(" ", "").replace("_", "").replace("-", "")
        s_cls = s["class_name"].lower().replace(" ", "").replace("_", "").replace("-", "")
        s_disp = s["display_name"].lower().replace(" ", "").replace("_", "").replace("-", "")
        if ident in (s_id, s_cls, s_disp) or s_id in ident or s_cls in ident:
            if s["src_path"].exists():
                return s["src_path"]
            static_path = Path(__file__).resolve().parent.parent / "static" / "samples" / s["filename"]
            if static_path.exists():
                return static_path
    raise HTTPException(status_code=404, detail=f"Sample '{identifier}' not found.")

@router.get("/samples/{sample_id}/image")
def get_sample_image(sample_id: str):
    file_path = resolve_sample_file(sample_id)
    return FileResponse(str(file_path), media_type="image/jpeg")


