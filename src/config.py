"""
Central configuration for Brain Tumor MRI AI classification project.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Base Paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
METRICS_DIR = RESULTS_DIR / "metrics"
CONFUSION_MATRICES_DIR = RESULTS_DIR / "confusion_matrices"
LOGS_DIR = RESULTS_DIR / "logs"

MODELS_DIR = PROJECT_ROOT / "models"
BEST_MODEL_PATH = MODELS_DIR / "resnet50_best.keras"

# Manifest Paths
TRAIN_MANIFEST = PROCESSED_DATA_DIR / "train_manifest.csv"
VAL_MANIFEST = PROCESSED_DATA_DIR / "val_manifest.csv"
TEST_MANIFEST = PROCESSED_DATA_DIR / "test_manifest.csv"

# Dataset Specs
CLASSES = ["glioma", "meningioma", "notumor", "pituitary"]
NUM_CLASSES = len(CLASSES)
CLASS_TO_IDX = {cls_name: i for i, cls_name in enumerate(CLASSES)}
IDX_TO_CLASS = {i: cls_name for i, cls_name in enumerate(CLASSES)}
CLASS_DISPLAY_NAMES = {
    "glioma": "Glioma Tumor",
    "meningioma": "Meningioma Tumor",
    "notumor": "No Tumor",
    "pituitary": "Pituitary Tumor"
}

# Image Specs
IMAGE_SIZE = (224, 224)
INPUT_SHAPE = (224, 224, 3)

# Training Hyperparameters
RANDOM_SEED = 42
BATCH_SIZE = 32
LEARNING_RATE = 1e-4
EPOCHS = 10
EARLY_STOPPING_PATIENCE = 4
REDUCE_LR_PATIENCE = 2
REDUCE_LR_FACTOR = 0.2
MIN_LR = 1e-6
VAL_SPLIT_RATIO = 0.15  # Stratified 15% of official training portion for validation

# Supported Image Formats
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
