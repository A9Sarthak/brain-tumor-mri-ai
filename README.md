# NEUROSCAN AI — Modern Clinical Web Platform for Brain MRI Analysis

[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16.3-black.svg)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4-38bdf8.svg)](https://tailwindcss.com)
[![Model](https://img.shields.io/badge/Model-EfficientNet--B0%20(80.00%25%20Test%20Acc)-success.svg)](https://keras.io)

NeuroScan AI is a production-style, clinical decision-support web platform for automated brain Magnetic Resonance Imaging (MRI) analysis. It couples a verified deep learning pipeline using **EfficientNet-B0** and **Grad-CAM interpretability** with a high-performance **FastAPI backend** and a clinical **Next.js + TypeScript + Tailwind CSS** frontend.

---

## 1. System Architecture

```
                                +---------------------------------------------+
                                |             Next.js 16 Frontend             |
                                |       TypeScript + Tailwind CSS (v4)        |
                                |                                             |
                                |  [Analyze]   [Insights]  [History]  [About] |
                                +----------------------+----------------------+
                                                       |
                                            REST API Requests (JSON / Multipart)
                                                       |
                                                       v
                                +---------------------------------------------+
                                |               FastAPI Backend               |
                                |                 (Port 8000)                 |
                                |                                             |
                                |  /api/health      /api/analyze              |
                                |  /api/gradcam     /api/performance          |
                                |  /api/samples     /api/report               |
                                +----------------------+----------------------+
                                                       |
                                              Direct Python Call
                                                       |
                                                       v
                                +---------------------------------------------+
                                |         Authoritative ML Pipeline           |
                                |                                             |
                                |  • Preprocessing: 224x224x3, RGB, 0-255     |
                                |  • Backbone: EfficientNet-B0                |
                                |  • Model Weights: best_efficientnet_model   |
                                |  • Layer top_conv -> Grad-CAM Heatmaps      |
                                |  • Output: Softmax (4 Classes)              |
                                +---------------------------------------------+
```

> **Model Protection Assurance:**
> The underlying EfficientNet-B0 model (`models/best_efficientnet_model.keras`) was pre-trained and fine-tuned in the prior phase. **It was strictly preserved with zero weight modifications, no retraining, and no changes to preprocessing or class mapping.**

---

## 2. Four Diagnostic Categories

The authoritative class indexing is locked to:

| Index | Clinical Class | Description |
| :--- | :--- | :--- |
| `0` | **No Tumor** | Healthy brain MRI scan showing normal anatomical symmetry without lesions. |
| `1` | **Glioma Tumor** | Infiltrative neoplastic tissue arising from glial cells (astrocytomas/glioblastomas). |
| `2` | **Meningioma Tumor** | Extra-axial, dural-attached lesions originating in arachnoid cap cells. |
| `3` | **Pituitary Tumor** | Neoplasms located in the sella turcica, adjacent to optic chiasm. |

---

## 3. Key Platform Features

### Frontend (Next.js + TypeScript + Tailwind CSS)
- **Clinical Aesthetics**: Minimalist, high-contrast, trustworthy design with curated medical colors (`#f8fafc` light mode, deep slate-950 dark mode).
- **No "Home" Navigation**: Header navigation is strictly organized into **Analyze**, **Insights**, **History**, and **About** (plus theme toggle).
- **Three-Part Workspace Workflow**:
  - `1. Upload MRI Scan`: Drag-and-drop zone with format verification (JPG/PNG, up to 200MB) and instant preview.
  - `2. AI Analysis Result`: Predicted condition, confidence score, and per-class probability breakdown bars.
  - `3. AI Explanation (Grad-CAM)`: Multi-tab visualizer with **Original**, **AI Attention**, and **Overlay** views extracted from layer `top_conv`.
- **Try an Example**: One-click real scan test for each of the 4 clinical classes.
- **Insights Page**: Displays held-out test benchmarks (80.00% accuracy, 79.10% Macro F1), confusion matrix, per-class metrics, and two-stage training history curves.
- **Session History**: Client-side session archive of analyzed scans with one-click report view and "Clear History" option.
- **Clinical Report Generator**: Formatted printable/copyable report with analysis ID, timestamps, class probabilities, and ethical AI statements.

### Backend (FastAPI + Python)
- **Singleton Model Loader**: EfficientNet-B0 is pre-warmed once at server startup and kept in memory.
- **RESTful Endpoints**:
  - `GET /api/health` — Returns model name, input shape, status, and class taxonomy.
  - `POST /api/analyze` — Receives MRI scan, runs inference, returns prediction, confidence, probabilities, and analysis ID.
  - `POST /api/gradcam` — Generates base64 heatmaps (Original, Attention, Overlay) for the predicted class.
  - `GET /api/performance` — Returns held-out test metrics and artifact URLs.
  - `GET /api/samples` — Provides sample scans for user testing.
  - `GET /api/samples/{id}/image` — Serves raw sample MRI scan file.
  - `POST /api/report` — Compiles official formatted clinical analysis report.

---

## 4. Setup & Running Locally

### Prerequisites
- **Python**: 3.10 or 3.11 (with "Add to PATH" checked)
- **Node.js**: 18+ LTS or 20+ LTS ([Download from nodejs.org](https://nodejs.org/))

---

### Step 1: First-Time Automatic Setup (Any New Device)

On any newly cloned device, run the automatic setup file:

- **Windows**: Double-click **`setup.bat`** (or run `setup.bat` in CMD / PowerShell)
- **macOS / Linux**: Run `./setup.sh`

This script will automatically:
1. Detect Python and create an isolated virtual environment (`.venv`).
2. Upgrade `pip` and install all required AI/ML + FastAPI dependencies from `requirements.txt`.
3. Detect Node.js and install all Next.js frontend packages (`npm install`).
4. Build the production-optimized Next.js frontend (`npm run build`).
5. Verify model weights and offer to launch the platform immediately.

---

### Step 2: Starting the Application

Once setup is complete, you can launch NeuroScan AI anytime:

#### Option A: One-Click Launcher (Recommended)
Double-click **`start.bat`** in the project root.
- Automatically launches the FastAPI backend in a separate terminal window.
- Automatically launches the Next.js frontend in a separate terminal window.
- Automatically opens **`http://localhost:3000`** in your default web browser!

#### Option B: Separate Launch Scripts
- **Start Backend**: Double-click `start_backend.bat` (serves API on `http://127.0.0.1:8000`)
- **Start Frontend**: Double-click `start_frontend.bat` (serves UI on `http://localhost:3000`)

#### Option C: Manual Terminal Commands

**Terminal 1 — Backend:**
```bash
# Windows
.venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000

# macOS / Linux
source .venv/bin/activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run start -- -p 3000
# or development mode:
npm run dev
```

---

## 5. Running with Docker Compose

```bash
docker-compose up --build
```
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

---

## 6. Running Tests

Run the full automated pytest suite (API tests and Model Regression tests):

```bash
.venv\Scripts\pytest -v tests/
```

Test coverage includes:
- Backend health, analyze, gradcam, performance, and report endpoints.
- Model singleton verification.
- Class mapping invariance check.
- Numerical equivalence and inference across all 4 sample scans.

---

## 7. Streamlit Co-existence

The legacy Streamlit application remains functional during the transition period:

```bash
streamlit run app/app.py --server.port 8501
```

---

## 8. Responsible AI & Medical Disclaimer

> **Clinical Research Notice:**
> NeuroScan AI is an academic and research decision-support prototype. It is **not a certified medical device** and should not be used as a sole diagnostic instrument for clinical patient care. All AI predictions must be correlated with histopathological, surgical, and clinical diagnostic findings by certified radiologists and physicians.
