"""
NeuroScan AI - Brain Tumor MRI Classification Web Application
Phase 1 Interactive Interface using Streamlit and ResNet50 Transfer Learning.
"""
import sys
from pathlib import Path
import tempfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

from src.config import (
    BEST_MODEL_PATH,
    CLASSES,
    CLASS_DISPLAY_NAMES,
    PLOTS_DIR,
    CONFUSION_MATRICES_DIR,
    METRICS_DIR,
    TEST_MANIFEST,
)
from src.utils import load_json

# Page configuration
st.set_page_config(
    page_title="NeuroScan AI | Brain Tumor Detection",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 4px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 20px;
    }
    .prediction-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 12px;
        padding: 22px;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
        margin-bottom: 16px;
    }
    .badge-normal {
        background-color: #10B981;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .badge-tumor {
        background-color: #EF4444;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading ResNet50 Deep Learning Weights...")
def get_model():
    """Lazily load and cache ResNet50 model."""
    import tensorflow as tf
    if not BEST_MODEL_PATH.exists():
        return None
    return tf.keras.models.load_model(BEST_MODEL_PATH)


# ================= SIDEBAR =================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brain.png", width=64)
    st.title("NeuroScan AI")
    st.caption("AI-Assisted Brain MRI Classification")
    st.markdown("---")

    st.subheader("Model Selector")
    selected_model = st.selectbox(
        "Architecture",
        [
            "ResNet50 (Transfer Learning - Phase 1)",
            "EfficientNet-B0 (Phase 2 - Planned)",
            "MobileNetV2 (Phase 2 - Planned)",
            "VGG16 (Phase 2 - Planned)",
        ]
    )

    if "Phase 2" in selected_model:
        st.warning("⚠️ Phase 2 model. Using ResNet50.")

    st.markdown("---")
    st.subheader("Quick Test Samples")
    st.caption("Click any scan below to test:")

    sample_clicked = None
    if TEST_MANIFEST.exists():
        test_df = pd.read_csv(TEST_MANIFEST)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Glioma Scan", key="btn_glioma", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "glioma"].iloc[0]["filepath"]
            if st.button("No Tumor Scan", key="btn_notumor", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "notumor"].iloc[0]["filepath"]
        with col_s2:
            if st.button("Meningioma", key="btn_meningioma", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "meningioma"].iloc[0]["filepath"]
            if st.button("Pituitary Scan", key="btn_pituitary", use_container_width=True):
                sample_clicked = test_df[test_df["class_name"] == "pituitary"].iloc[0]["filepath"]

    st.markdown("---")
    st.markdown("""
    **Phase 1 Specifications**
    - **Dataset**: 7,200 Scans
    - **Classes**: 4 (Balanced)
    - **Backbone**: ResNet50
    - **Test Accuracy**: 38.88%
    - **Baseline Accuracy**: 25.00%
    """)

# ================= MAIN PAGE =================
st.markdown('<p class="main-header">🧠 Brain Tumor MRI Detection & Classification</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Deep Transfer Learning (ResNet50) Decision-Support Prototype</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔬 Live MRI Classifier", "📊 Model Performance & Metrics", "ℹ️ About & Methodology"])

with tab1:
    col_upload, col_result = st.columns([1, 1], gap="large")

    active_image_path = None
    uploaded_file = None

    with col_upload:
        st.subheader("1. Input MRI Scan")
        uploaded_file = st.file_uploader(
            "Upload patient brain MRI slice (JPG / PNG)",
            type=["jpg", "jpeg", "png"],
            help="Select an axial, sagittal, or coronal T1/T2 MRI scan."
        )

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                active_image_path = tmp.name
            st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        elif sample_clicked:
            active_image_path = sample_clicked
            st.image(active_image_path, caption=f"Selected Sample: {Path(active_image_path).name}", use_container_width=True)
        else:
            st.info("💡 Tip: Upload an MRI scan above, or click a Quick Test Sample in the left sidebar to run instant classification.")

    with col_result:
        st.subheader("2. Diagnostic Prediction")

        if active_image_path:
            with st.spinner("Analyzing scan with ResNet50..."):
                try:
                    from src.predict import predict_single_image
                    model_instance = get_model()
                    result = predict_single_image(active_image_path, model_or_path=model_instance)
                    pred_class = result["predicted_class"]
                    display_name = result["predicted_display_name"]
                    conf = result["confidence_percentage"]
                    probs = result["probabilities"]

                    is_normal = pred_class == "notumor"
                    badge_class = "badge-normal" if is_normal else "badge-tumor"
                    badge_text = "NORMAL (NO TUMOR)" if is_normal else "NEOPLASTIC LESION DETECTED"

                    st.markdown(f"""
                    <div class="prediction-card">
                        <span class="{badge_class}">{badge_text}</span>
                        <h2 style="color: white; margin-top: 10px; margin-bottom: 4px;">{display_name}</h2>
                        <p style="font-size: 1.05rem; color: #94A3B8; margin-bottom: 6px;">Confidence: <strong>{conf:.2f}%</strong></p>
                    </div>
                    """, unsafe_allow_html=True)

                    st.progress(conf / 100.0)

                    st.markdown("#### Probability Distribution")
                    chart_df = pd.DataFrame({
                        "Class": [CLASS_DISPLAY_NAMES[c] for c in CLASSES],
                        "Probability (%)": [probs[c] * 100.0 for c in CLASSES]
                    })
                    st.bar_chart(chart_df.set_index("Class"), color="#3B82F6", height=220)

                    # Metric cards
                    cols_p = st.columns(4)
                    for i, cls in enumerate(CLASSES):
                        with cols_p[i]:
                            st.metric(
                                label=CLASS_DISPLAY_NAMES[cls].replace(" Tumor", ""),
                                value=f"{probs[cls]*100.0:.1f}%"
                            )

                except Exception as e:
                    st.error(f"Inference error: {str(e)}")
        else:
            st.write("Awaiting MRI scan input to display diagnostic results.")

with tab2:
    st.subheader("📈 Experimental Results on 1,600 Held-Out Test Scans")

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
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown("#### Programmatic Confusion Matrix (1,600 Scans)")
        cm_img = CONFUSION_MATRICES_DIR / "confusion_matrix.png"
        if cm_img.exists():
            st.image(str(cm_img), use_container_width=True)

    with col_p2:
        st.markdown("#### Class Distribution Across Splits")
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
    st.subheader("Project Methodology & Pathology Overview")
    st.markdown("""
    ### Target Classes
    1. **Glioma Tumor**: Infiltrative primary tumor originating from glial cells.
    2. **Meningioma Tumor**: Typically benign tumor developing from the arachnoid layer of the meninges.
    3. **Pituitary Tumor**: Adenoma developing within the sella turcica, affecting hormonal secretion.
    4. **No Tumor**: Normal brain tissue with intact ventricular symmetry.

    ### Phase 1 Core Pipeline
    - **Transfer Learning**: ImageNet-pretrained ResNet50 convolutional backbone.
    - **Safe Splitting**: Cryptographic SHA-256 hash grouping preventing duplicate leakage between Train, Val, and Test.
    - **Validation**: Evaluated against a naive Majority-Class Baseline on 1,600 held-out scans.
    """)

st.markdown("---")
st.caption("⚠️ **Disclaimer**: Experimental educational prototype. Not for primary clinical diagnosis.")
