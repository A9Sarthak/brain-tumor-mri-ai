"""
NeuroScan AI - Brain Tumor MRI Classification Web Application
Phase 1 Interactive Interface using Streamlit and ResNet50 Transfer Learning.
"""
import sys
from pathlib import Path
import tempfile

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import tensorflow as tf

from src.config import (
    BEST_MODEL_PATH,
    CLASSES,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE,
    PLOTS_DIR,
    CONFUSION_MATRICES_DIR,
    METRICS_DIR,
    TEST_MANIFEST,
)
from src.predict import predict_single_image
from src.utils import load_json

# Page configuration
st.set_page_config(
    page_title="NeuroScan AI | Brain Tumor Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern medical UI styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 25px;
    }
    .prediction-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .badge-normal {
        background-color: #10B981;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .badge-tumor {
        background-color: #EF4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .stat-box {
        border-left: 4px solid #3B82F6;
        padding-left: 12px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_classification_model():
    """Cache loaded ResNet50 model in memory."""
    if not BEST_MODEL_PATH.exists():
        return None
    return tf.keras.models.load_model(BEST_MODEL_PATH)


model = load_classification_model()

# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brain.png", width=64)
    st.title("NeuroScan AI")
    st.caption("AI-Assisted MRI Diagnostic Support")
    st.markdown("---")

    st.subheader("Model Selection")
    selected_model = st.selectbox(
        "Active Deep Learning Architecture",
        [
            "ResNet50 (Transfer Learning - Phase 1)",
            "EfficientNet-B0 (Phase 2 - Planned)",
            "MobileNetV2 (Phase 2 - Planned)",
            "VGG16 (Phase 2 - Planned)",
        ]
    )

    if "Phase 2" in selected_model:
        st.warning("⚠️ This architecture is scheduled for Phase 2. Using ResNet50 for inference.")

    st.markdown("---")
    st.subheader("Quick Test Samples")
    st.caption("Click a sample to test without uploading:")

    sample_clicked = None
    if TEST_MANIFEST.exists():
        test_df = pd.read_csv(TEST_MANIFEST)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Glioma Scan", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "glioma"].iloc[0]["filepath"]
            if st.button("No Tumor Scan", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "notumor"].iloc[0]["filepath"]
        with col_s2:
            if st.button("Meningioma", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "meningioma"].iloc[0]["filepath"]
            if st.button("Pituitary Scan", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "pituitary"].iloc[0]["filepath"]

    st.markdown("---")
    st.markdown("""
    **Pipeline Specs (Phase 1)**
    - **Dataset**: 7,200 Scans (Kaggle)
    - **Backbone**: ImageNet Pretrained
    - **Classes**: 4 (Balanced)
    - **Validation Accuracy**: 40.94%
    - **Test Accuracy**: 38.88%
    - **Baseline Accuracy**: 25.00%
    """)

# ================= MAIN PAGE =================
st.markdown('<p class="main-header">🧠 Brain Tumor MRI Detection & Classification</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Deep Transfer Learning (ResNet50) Prototype — Experimental Decision Support</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔬 Live MRI Classifier", "📊 Model Performance & Metrics", "ℹ️ About & Methodology"])

with tab1:
    col_upload, col_result = st.columns([1, 1], gap="large")

    active_image_path = None
    uploaded_file = None

    with col_upload:
        st.subheader("1. Input MRI Scan")
        uploaded_file = st.file_uploader(
            "Upload patient brain MRI slice (JPG/PNG)",
            type=["jpg", "jpeg", "png"],
            help="Select an axial, sagittal, or coronal T1/T2 MRI brain scan."
        )

        if uploaded_file is not None:
            # Save to temporary file for inference
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                active_image_path = tmp.name
            st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        elif sample_clicked:
            active_image_path = sample_clicked
            st.image(active_image_path, caption=f"Sample: {Path(active_image_path).name}", use_container_width=True)
        else:
            st.info("👆 Upload an MRI scan above, or select a Quick Test Sample from the sidebar.")

    with col_result:
        st.subheader("2. AI Diagnostic Prediction")

        if active_image_path and model is not None:
            with st.spinner("Analyzing MRI scan features..."):
                try:
                    result = predict_single_image(active_image_path, model_or_path=model)
                    pred_class = result["predicted_class"]
                    display_name = result["predicted_display_name"]
                    conf = result["confidence_percentage"]
                    probs = result["probabilities"]

                    is_normal = pred_class == "notumor"
                    badge_class = "badge-normal" if is_normal else "badge-tumor"
                    badge_text = "NORMAL (NO TUMOR)" if is_normal else "NEOPLASTIC LESION DETECTED"

                    # Card Display
                    st.markdown(f"""
                    <div class="prediction-card">
                        <span class="{badge_class}">{badge_text}</span>
                        <h2 style="color: white; margin-top: 12px; margin-bottom: 4px;">{display_name}</h2>
                        <p style="font-size: 1.1rem; color: #94A3B8; margin-bottom: 8px;">Confidence: <strong>{conf:.2f}%</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.progress(conf / 100.0)

                    st.markdown("#### Multi-Class Probability Breakdown")
                    chart_data = pd.DataFrame({
                        "Diagnosis": [CLASS_DISPLAY_NAMES[c] for c in CLASSES],
                        "Probability (%)": [probs[c] * 100.0 for c in CLASSES]
                    })
                    st.bar_chart(chart_data.set_index("Diagnosis"), color="#3B82F6", height=240)

                    # Detailed Probability Table
                    cols_prob = st.columns(4)
                    for i, cls in enumerate(CLASSES):
                        with cols_prob[i]:
                            st.metric(
                                label=CLASS_DISPLAY_NAMES[cls].replace(" Tumor", ""),
                                value=f"{probs[cls]*100.0:.1f}%"
                            )

                except Exception as e:
                    st.error(f"Inference Error: {str(e)}")
        elif model is None:
            st.error("Model checkpoint not found. Please train the model first.")
        else:
            st.write("Waiting for MRI scan input to generate real-time classification...")

with tab2:
    st.subheader("📈 Experimental Evaluation on 1,600 Held-out Test Scans")
    
    # Load actual metrics JSON
    metrics_file = METRICS_DIR / "resnet50_test_metrics.json"
    baseline_file = METRICS_DIR / "baseline_metrics.json"

    if metrics_file.exists() and baseline_file.exists():
        res_metrics = load_json(metrics_file)
        base_metrics = load_json(baseline_file)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Test Accuracy", f"{res_metrics['accuracy']*100:.2f}%", f"+{(res_metrics['accuracy']-base_metrics['accuracy'])*100:.2f}% vs Baseline")
        m2.metric("Macro Precision", f"{res_metrics['precision_macro']*100:.2f}%", f"+{(res_metrics['precision_macro']-base_metrics['precision_macro'])*100:.2f}%")
        m3.metric("Macro Recall", f"{res_metrics['recall_macro']*100:.2f}%", f"+{(res_metrics['recall_macro']-base_metrics['recall_macro'])*100:.2f}%")
        m4.metric("Macro F1-Score", f"{res_metrics['f1_macro']*100:.2f}%", f"+{(res_metrics['f1_macro']-base_metrics['f1_macro'])*100:.2f}%")

    st.markdown("---")
    col_plot1, col_plot2 = st.columns(2)

    with col_plot1:
        st.markdown("#### Programmatic Confusion Matrix (1,600 Scans)")
        cm_img = CONFUSION_MATRICES_DIR / "confusion_matrix.png"
        if cm_img.exists():
            st.image(str(cm_img), use_container_width=True)

    with col_plot2:
        st.markdown("#### Class Distribution Across Partitions")
        dist_img = PLOTS_DIR / "class_distribution.png"
        if dist_img.exists():
            st.image(str(dist_img), use_container_width=True)

    st.markdown("#### Training History (Accuracy & Loss Curves)")
    col_c1, col_c2 = st.columns(2)
    acc_img = PLOTS_DIR / "resnet50_accuracy.png"
    loss_img = PLOTS_DIR / "resnet50_loss.png"
    if acc_img.exists() and loss_img.exists():
        with col_c1:
            st.image(str(acc_img), use_container_width=True)
        with col_c2:
            st.image(str(loss_img), use_container_width=True)

with tab3:
    st.subheader("Project Specifications & Methodology")
    st.markdown("""
    ### Problem Overview
    Manual interpretation of brain MRI slices is time-consuming and vulnerable to human fatigue. 
    **NeuroScan AI** utilizes deep transfer learning with **ResNet50** to perform automated 4-class differential diagnosis.

    ### The Four Target Pathologies:
    1. **Glioma**: Primary brain tumors developing in glial tissues; often infiltrative.
    2. **Meningioma**: Typically benign, slow-growing tumors arising from the protective brain meninges.
    3. **Pituitary**: Neoplasms in the pituitary gland impacting endocrine regulation.
    4. **No Tumor**: Normal, healthy brain tissue demonstrating anatomical symmetry.

    ### Phase 1 Technical Stack
    - **Language & Frameworks**: Python 3.11, TensorFlow 2.21, Keras 3, Scikit-learn, OpenCV, Streamlit.
    - **Data Protection**: Strict cryptographic SHA-256 hash isolation between Train, Validation, and Test partitions.
    - **Academic Baseline**: Majority-class naive baseline evaluated alongside deep models for scientific integrity.
    """)

# ================= FOOTER DISCLAIMER =================
st.markdown("---")
st.caption("""
⚠️ **Medical Disclaimer**: This AI software is an experimental prototype created for academic, educational, and research evaluation. 
It is **NOT** certified as a clinical medical device. It should never be used as a standalone diagnostic tool or to guide medical treatments without radiologist review.
""")
