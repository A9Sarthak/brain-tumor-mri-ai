# Brain Tumor Detection from MRI Images using Transfer Learning-based CNN Models

![Python Version](https://img.shields.io/badge/Python-3.11.9-blue.svg)
![TensorFlow Version](https://img.shields.io/badge/TensorFlow-2.21.0-orange.svg)
![Tests](https://img.shields.io/badge/Tests-21%20Passed-brightgreen.svg)
![Phase](https://img.shields.io/badge/Status-Phase%201%20Complete%20(60%25)-green.svg)

---

## 1. Project Overview
This repository contains the core deep learning implementation for automated classification of brain tumors from Magnetic Resonance Imaging (MRI) scans. Leveraging transfer learning with deep convolutional neural networks (CNNs), the system analyzes brain scans and categorizes them into four distinct clinical classes: **Glioma Tumor**, **Meningioma Tumor**, **Pituitary Tumor**, and **No Tumor (Normal)**.

---

## 2. Problem Statement
Brain tumors represent one of the most critical neurological disorders where early and accurate diagnosis directly governs treatment efficacy and patient survival. Traditional diagnosis relies heavily on radiologists manually inspecting hundreds of MRI slice sequences. This manual workflow is time-intensive, subject to cognitive fatigue, and susceptible to inter-observer variability. An automated AI-assisted second-opinion tool provides objective, reproducible classification support.

---

## 3. Objectives
- **Phase 1 Objective**: Develop a robust, leak-free AI/ML pipeline featuring dataset verification, persistent stratified partitioning, modular preprocessing, ResNet50 transfer learning, automated metric evaluation against a naive baseline, model checkpointing, single-image inference, and unit testing.
- **Eventual Phase 2 Objective**: Train and systematically benchmark four CNN architectures (ResNet50, EfficientNet-B0, MobileNetV2, VGG16), integrate visual explainability via Grad-CAM thermal heatmaps, and deploy an interactive web interface.

---

## 4. Four Classification Classes
| Class Identifier | Clinical Description | Pathological Characteristics |
| :--- | :--- | :--- |
| `glioma` | Glioma Tumor | Originates in glial cells of the brain and spinal cord; often infiltrative. |
| `meningioma` | Meningioma Tumor | Arises from the meninges (membranes enveloping brain and spinal cord). |
| `notumor` | No Tumor (Normal) | Healthy brain MRI scan showing anatomical symmetry and no neoplastic lesions. |
| `pituitary` | Pituitary Tumor | Develops in the pituitary gland at the skull base; affects endocrine function. |

---

## 5. Proposed AI Method
The system processes raw brain MRI scans through a standardized computer vision pipeline:
```
Raw MRI Scan (JPG/PNG)
        ↓
Image Verification & Integrity Check
        ↓
Resolution Standardization (224 x 224 x 3)
        ↓
Model-Specific Preprocessing (Zero-Centering around ImageNet Channel Means)
        ↓
Pretrained CNN Feature Extractor (ResNet50 Backbone - Frozen)
        ↓
Global Average Pooling 2D
        ↓
Dense Feature Head (256 units, ReLU) + Batch Normalization + Dropout (0.4)
        ↓
Dense Softmax Classifier (4 units)
        ↓
Class Probabilities: [P(glioma), P(meningioma), P(notumor), P(pituitary)]
```

---

## 6. Transfer Learning Approach
Training deep neural networks from scratch on specialized medical imagery often causes severe overfitting due to limited sample sizes. Transfer learning circumvents this limitation by repurposing the rich feature representations learned by deep CNNs on millions of natural images (ImageNet). In Phase 1, the **ResNet50** convolutional backbone is frozen as a feature extractor, training only the newly attached classification head.

---

## 7. Dataset
- **Source**: Kaggle `masoudnickparvar/brain-tumor-mri-dataset` (Version 2)
- **Total Discovered Images**: 7,200 images (100% verified valid, 0 corrupt/unreadable files)
- **Image Formats**: JPEG (`.jpg`)
- **Dimensions**: Variable aspect ratios (e.g. 200x252, 512x512), standardized to $224 \times 224 \times 3$
- **Partitions & Distribution**:
  - **Training Split**: 4,767 images
  - **Validation Split**: 833 images
  - **Held-out Test Split**: 1,600 images (100% preserved official test split)
- **Data Leakage Safeguards**: Partitioning incorporates cryptographic SHA-256 hash grouping. Zero duplicate image hashes exist across splits ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).

---

## 8. Preprocessing & Augmentation
- **Modular Preprocessing**: Implemented in `src/preprocessing.py`, centering RGB tensors around ImageNet channel means.
- **Training-Only Augmentation**:
  - Random Horizontal Flip
  - Random Rotation ($\pm 10^\circ$)
  - Random Zoom ($\pm 8\%$)
  - Random Contrast Adjustment ($\pm 10\%$)
- **Validation & Test Pipelines**: Strictly deterministic resizing and normalization without augmentation.

---

## 9. ResNet50 Model Architecture
- **Backbone**: ImageNet-pretrained `ResNet50` without top layers (`input_shape=(224, 224, 3)`)
- **Backbone Status**: Frozen (`trainable=False`)
- **Total Parameters**: 24,114,308 (91.99 MB)
- **Trainable Parameters**: 526,084 (Classification Head)
- **Non-Trainable Parameters**: 23,588,224 (Frozen Backbone)

---

## 10. Training Procedure
- **Optimizer**: Adam ($\text{learning rate} = 10^{-4}$)
- **Loss Function**: Sparse Categorical Crossentropy
- **Batch Size**: 64
- **Epochs Trained**: 3
- **Callbacks**:
  - `ModelCheckpoint`: Automatically saves best model to `models/resnet50_best.keras` based on validation loss.
  - `ReduceLROnPlateau`: Halves learning rate upon plateau.
  - `EarlyStopping`: Prevents overfitting by restoring best epoch weights.
- **Execution Device**: Intel(R) Core CPU (Windows native environment; GPU Available: False)
- **Training Duration**: 6 minutes 59 seconds
- **Best Validation Epoch**: Epoch 1 ($\text{Val Loss} = 1.5242$, $\text{Val Accuracy} = 40.94\%$)

---

## 11. Experimental Evaluation Results
All values reported below are derived from actual execution on the 1,600 held-out test scans:

| Metric | Majority-Class Baseline | ResNet50 (Phase 1 Transfer Learning) |
| :--- | :---: | :---: |
| **Accuracy** | 25.00% | **38.88%** |
| **Macro Precision** | 6.25% | **32.28%** |
| **Weighted Precision** | 6.25% | **32.28%** |
| **Macro Recall** | 25.00% | **38.88%** |
| **Weighted Recall** | 25.00% | **38.88%** |
| **Macro F1-Score** | 10.00% | **28.83%** |
| **Weighted F1-Score** | 10.00% | **28.83%** |

### Detailed Classification Report (Held-out Test Set)
```
              precision    recall  f1-score   support

      glioma       0.18      0.04      0.07       400
  meningioma       0.29      0.56      0.39       400
     notumor       0.52      0.93      0.67       400
   pituitary       0.30      0.01      0.03       400

    accuracy                           0.39      1600
   macro avg       0.32      0.39      0.29      1600
weighted avg       0.32      0.39      0.29      1600
```

---

## 12. Single-Image Inference
The inference module (`src/predict.py`) accepts any brain MRI image, verifies its integrity, applies preprocessing, and outputs the predicted diagnosis, confidence percentage, and complete 4-class probability distribution:

```powershell
python -m src.predict --image data/raw/Testing/notumor/Te-no_1.jpg
```
**Example Output**:
```
=============================================
BRAIN TUMOR MRI PREDICTION
=============================================
File: Te-no_1.jpg
Image Dimensions: 200 x 252 px
---------------------------------------------
Prediction: No Tumor (notumor)
Confidence: 68.49%
---------------------------------------------
Probabilities:
  Glioma Tumor        : 29.81%
  Meningioma Tumor    : 1.60%
  No Tumor            : 68.49%
  Pituitary Tumor     : 0.11%
=============================================
```

---

## 13. Project Structure
```
brain-tumor-mri-ai/
│
├── data/
│   ├── raw/                  # Downloaded raw MRI dataset (excluded from Git)
│   ├── processed/            # Deterministic persistent split manifests (CSV)
│   └── README.md             # Dataset documentation and provenance
│
├── src/
│   ├── __init__.py
│   ├── config.py             # Central paths, hyperparameters, class mappings
│   ├── data_loader.py        # Dataset discovery, verification, persistent splitting
│   ├── preprocessing.py      # Modular resizing, normalization, and augmentation
│   ├── models.py             # ResNet50 transfer learning architecture
│   ├── train.py              # Two-stage training pipeline (smoke test & full run)
│   ├── evaluate.py           # Test set evaluation, metrics, and baseline comparison
│   ├── predict.py            # Single-image inference module
│   └── utils.py              # Reproducibility seeds, plotting, hardware detection
│
├── tests/
│   ├── conftest.py           # Pytest path configuration
│   ├── test_dataset.py       # Dataset integrity, structure, and corruption handling
│   ├── test_data_leakage.py  # Zero-leakage set intersection & hash duplicate tests
│   ├── test_preprocessing.py # Tensor shapes, normalization, and augmentation
│   ├── test_model.py         # ResNet50 construction, layer freeze, softmax sums
│   ├── test_predict.py       # Output schema, class bounds, probability summation
│   ├── test_storage.py       # Checkpoint save, clean reload, prediction consistency
│   └── test_edge_cases.py    # Corrupt images, zero-byte files, invalid paths
│
├── results/
│   ├── plots/                # Class distribution, accuracy, and loss curves
│   ├── metrics/              # Classification metrics JSON and text reports
│   ├── confusion_matrices/   # Heatmap confusion matrix plots
│   └── logs/                 # Training histories and execution logs
│
├── models/
│   ├── .gitkeep
│   └── resnet50_best.keras   # Saved model checkpoint (best validation loss)
│
├── requirements.txt          # Pinned minimum dependencies
├── .gitignore                # Comprehensive version control exclusions
└── README.md                 # Complete project documentation
```

---

## 14. Installation
```powershell
# Clone repository
git clone https://github.com/A9Sarthak/brain-tumor-mri-ai.git
cd brain-tumor-mri-ai

# Create and activate Python 3.11 virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## 15. Usage Instructions
```powershell
# 1. Inspect and partition dataset
python -m src.data_loader --inspect

# 2. Run Stage A Smoke Test (quick verification on 16 images)
python -m src.train --smoke-test

# 3. Run Stage B Full Training & Evaluation
python -m src.train --epochs 3 --batch-size 64

# 4. Evaluate trained model independently
python -m src.evaluate

# 5. Predict single MRI image
python -m src.predict --image data/raw/Testing/notumor/Te-no_1.jpg
```

---

## 16. Automated Testing
Run the complete unit test suite:
```powershell
pytest tests/ -v
```
**Results**:
- **Tests Executed**: 21
- **Passed**: 21
- **Failed**: 0
- **Skipped**: 0

---

## 17. Current Phase 1 Status
Phase 1 is approximately **60% complete**. The core deep learning pipeline is genuinely implemented, verified, and functional:
- [x] Environment inspected and documented
- [x] GitHub authentication verified (`A9Sarthak`) and repository created
- [x] Full dataset verified (7,200 images, 0 corrupt files)
- [x] Persistent split manifests generated with zero hash leakage
- [x] Automated leakage test created and verified
- [x] Modular preprocessing and training augmentation implemented
- [x] ResNet50 transfer learning model constructed and compiled
- [x] Stage A smoke test executed successfully
- [x] Stage B full experiment completed on all valid training images
- [x] Held-out test evaluation completed and plotted
- [x] Model save and clean reload consistency verified
- [x] Single-image inference tested and verified
- [x] Automated test suite (21/21 passing)

---

## 18. Planned Phase 2 Work (Pending Explicit User Instruction)
The following components are strictly deferred to Phase 2:
1. Implementation and training of **EfficientNet-B0**.
2. Implementation and training of **MobileNetV2**.
3. Implementation and training of **VGG16**.
4. Multi-model comparative benchmarking across identical data splits.
5. Final best model selection.
6. **Grad-CAM** visual interpretability engine generating gradient heatmaps.
7. Interactive **Streamlit** browser application for clinical review.
8. Packaging, comprehensive final documentation, report, and presentation slides.

---

## 19. Limitations
- **Device Throughput**: Native Windows execution of TensorFlow >= 2.11 operates on CPU; GPU acceleration requires WSL2 or TensorFlow-DirectML.
- **Backbone Fine-Tuning**: In Phase 1, the ResNet50 backbone is frozen to establish head weights; unfreezing top residual blocks for fine-tuning with a lower learning rate is reserved for Phase 2.
- **Single Architecture**: Performance comparison is not yet available as only ResNet50 has been trained in Phase 1.

---

## 20. Medical and Educational Disclaimer
This software is an **experimental academic prototype** developed exclusively for educational and research purposes. It is **NOT** a certified medical diagnostic device and has not been clinically validated. It must **NOT** be used as a substitute for professional clinical diagnosis, radiological assessment, or patient treatment decisions.
