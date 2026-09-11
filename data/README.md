# Brain Tumor MRI Dataset

## Provenance
- **Source**: Kaggle `masoudnickparvar/brain-tumor-mri-dataset`
- **Revision / Version**: Version 2
- **Acquisition Tool**: `kagglehub.dataset_download('masoudnickparvar/brain-tumor-mri-dataset')`
- **License**: CC BY-SA 4.0 / Public Dataset

## Target Classes (4)
1. `glioma` — Glioma Tumor
2. `meningioma` — Meningioma Tumor
3. `notumor` — No Tumor (Normal)
4. `pituitary` — Pituitary Tumor

## Structure
- `data/raw/Training/`: Official training split containing 4 subfolders (`glioma`, `meningioma`, `notumor`, `pituitary`).
- `data/raw/Testing/`: Official held-out test split containing 4 subfolders (`glioma`, `meningioma`, `notumor`, `pituitary`).
- `data/processed/`: Deterministic persistent CSV manifests (`train_manifest.csv`, `val_manifest.csv`, `test_manifest.csv`) with exact paths, labels, and SHA-256 hashes.

## Safety & Exclusion
Raw MRI image data is strictly excluded from version control via `.gitignore`.
