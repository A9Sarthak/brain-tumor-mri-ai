"""
Download the authoritative Brain Tumor MRI dataset from Kaggle directly into data/raw/
"""
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_RAW_DIR = PROJECT_ROOT / "data" / "raw"

def download_dataset():
    print("=" * 60)
    print("NeuroScan AI - Automated Dataset Downloader")
    print("Dataset: masoudnickparvar/brain-tumor-mri-dataset (Kaggle)")
    print("=" * 60)
    
    try:
        import kagglehub
    except ImportError:
        print("[ERROR] kagglehub is not installed.")
        print("Please run: pip install kagglehub")
        sys.exit(1)

    print("\n[1/3] Downloading dataset via kagglehub...")
    try:
        download_cache = kagglehub.dataset_download("masoudnickparvar/brain-tumor-mri-dataset")
        print(f"[OK] Downloaded to cache: {download_cache}")
    except Exception as e:
        print(f"[ERROR] Failed to download via kagglehub: {e}")
        print("\nAlternative manual method:")
        print("1. Download directly from: https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset")
        print(f"2. Extract the files directly into: {TARGET_RAW_DIR}")
        sys.exit(1)

    src_path = Path(download_cache)
    TARGET_RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[2/3] Moving files into project data/raw/ ...")
    # Check if download_cache contains Training and Testing
    training_src = src_path / "Training"
    testing_src = src_path / "Testing"

    if training_src.exists() and testing_src.exists():
        for split in ["Training", "Testing"]:
            dest = TARGET_RAW_DIR / split
            if dest.exists():
                print(f"Destination {dest} already exists, skipping copy.")
            else:
                shutil.copytree(src_path / split, dest)
                print(f"[OK] Copied {split} -> {dest}")
    else:
        # Fallback: copy everything inside src_path
        for item in src_path.iterdir():
            dest = TARGET_RAW_DIR / item.name
            if not dest.exists():
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
                print(f"[OK] Copied {item.name} -> {dest}")

    print("\n[3/3] Verifying dataset structure...")
    tr_count = len(list((TARGET_RAW_DIR / "Training").rglob("*.jpg"))) if (TARGET_RAW_DIR / "Training").exists() else 0
    te_count = len(list((TARGET_RAW_DIR / "Testing").rglob("*.jpg"))) if (TARGET_RAW_DIR / "Testing").exists() else 0
    print(f"  - Training scans found: {tr_count}")
    print(f"  - Testing scans found:  {te_count}")
    print("\n[SUCCESS] Dataset is ready in data/raw/!")

if __name__ == "__main__":
    download_dataset()
