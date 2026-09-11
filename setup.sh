#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================"
echo "        NEUROSCAN AI - AUTOMATED PROJECT SETUP"
echo "============================================================"
echo ""
echo "This script will configure your system to run NeuroScan AI:"
echo "  1. Detect Python and create isolated virtual environment (.venv)"
echo "  2. Install all required AI/ML & Backend dependencies"
echo "  3. Detect Node.js and install Next.js frontend packages"
echo "  4. Build the production frontend bundle"
echo ""

# 1. Python check
echo "[1/5] Checking Python installation..."
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "[ERROR] Python was not found. Please install Python 3.10+."
    exit 1
fi
echo "Detected: $($PY_CMD --version)"

# 2. Virtual environment
echo ""
echo "[2/5] Setting up Python virtual environment (.venv)..."
if [ ! -f ".venv/bin/python" ]; then
    $PY_CMD -m venv .venv
    echo "Virtual environment created."
else
    echo "Existing .venv found."
fi

# 3. Dependencies
echo ""
echo "[3/5] Installing Python dependencies..."
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt

# 4. Node.js & Frontend
echo ""
echo "[4/5] Checking Node.js and installing frontend packages..."
if ! command -v node &>/dev/null; then
    echo "[ERROR] Node.js is required. Please install Node.js (v18+) from https://nodejs.org/"
    exit 1
fi
echo "Detected Node.js: $(node -v)"

cd frontend
npm install
npm run build
cd ..

# 5. Model weights check
echo ""
echo "[5/5] Verifying AI model weights..."
if [ -f "models/best_efficientnet_model.keras" ]; then
    echo "AI model weights detected: models/best_efficientnet_model.keras"
else
    echo "[NOTICE] 'models/best_efficientnet_model.keras' not found."
    echo "Please place your model weights file into the models/ folder."
fi

echo ""
echo "============================================================"
echo "        NEUROSCAN AI SETUP COMPLETED SUCCESSFULLY!"
echo "============================================================"
echo "To run the backend:"
echo "  source .venv/bin/activate && uvicorn backend.main:app --host 127.0.0.1 --port 8000"
echo ""
echo "To run the frontend:"
echo "  cd frontend && npm run start -- -p 3000"
echo "============================================================"
