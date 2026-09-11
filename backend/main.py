import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import shutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.routes.health import router as health_router
from backend.routes.analyze import router as analyze_router
from backend.routes.performance import router as performance_router
from backend.routes.samples import router as samples_router
from backend.routes.report import router as report_router
from backend.services.model_service import ModelService
from src.config import RESULTS_DIR, RAW_DATA_DIR

app = FastAPI(
    title="NeuroScan AI Medical API",
    description="Production-grade AI Brain MRI Classification & Grad-CAM Interpretability Engine",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files Setup
static_dir = Path(__file__).resolve().parent / "static"
samples_dir = static_dir / "samples"
samples_dir.mkdir(parents=True, exist_ok=True)

# Copy 4 representative test scans to static samples directory
sample_mappings = {
    "Te-gl_1.jpg": RAW_DATA_DIR / "Testing" / "glioma" / "Te-gl_1.jpg",
    "Te-me_1.jpg": RAW_DATA_DIR / "Testing" / "meningioma" / "Te-me_1.jpg",
    "Te-no_1.jpg": RAW_DATA_DIR / "Testing" / "notumor" / "Te-no_1.jpg",
    "Te-pi_1.jpg": RAW_DATA_DIR / "Testing" / "pituitary" / "Te-pi_1.jpg",
}

for dest_name, src_path in sample_mappings.items():
    dest_path = samples_dir / dest_name
    if src_path.exists() and not dest_path.exists():
        shutil.copyfile(src_path, dest_path)

# Mount Static Directories
app.mount("/static/samples", StaticFiles(directory=str(samples_dir)), name="samples")
if RESULTS_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(RESULTS_DIR)), name="results")

# Include Routers
app.include_router(health_router)
app.include_router(analyze_router)
app.include_router(performance_router)
app.include_router(samples_router)
app.include_router(report_router)

@app.on_event("startup")
def startup_event():
    print("[FastAPI] Initializing NeuroScan AI backend...")
    # Pre-warm model singleton
    ModelService.get_instance()
    print("[FastAPI] Backend initialization complete. Model ready for inference.")

@app.get("/")
def root():
    return {
        "service": "NeuroScan AI API",
        "status": "online",
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
