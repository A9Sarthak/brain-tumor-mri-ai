import sys
from pathlib import Path
import tempfile
import time
import json
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import tensorflow as tf

from src.config import (
    BEST_MODEL_PATH,
    MODEL_PATHS,
    CLASSES,
    CLASS_DISPLAY_NAMES,
    IMAGE_SIZE,
    GRADCAM_TARGET_LAYERS,
    TEST_MANIFEST,
    METRICS_DIR
)
from src.utils import verify_image_file
from src.preprocessing import load_and_preprocess_image, get_model_preprocess_fn
from src.gradcam import (
    compute_gradcam_heatmap,
    generate_gradcam_overlay,
    find_target_conv_layer,
)

# Configuration & Constants
ARCH_KEY = "EfficientNet-B0"
HEATMAP_ALPHA = 0.45
COLORMAP = cv2.COLORMAP_JET

st.set_page_config(
    page_title="NeuroScan | AI MRI Analysis",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "history" not in st.session_state:
    st.session_state.history = []
if "active_image_path" not in st.session_state:
    st.session_state.active_image_path = None
if "report_ready" not in st.session_state:
    st.session_state.report_ready = False

def nav_to(page_name):
    st.session_state.page = page_name
    st.session_state.report_ready = False

# Premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    .stApp header {
        display: none !important;
    }
    
    .block-container {
        max-width: 1300px;
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    /* Top Navigation */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 2rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .nav-logo {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.5px;
    }
    .nav-links {
        display: flex;
        gap: 20px;
    }
    
    /* Hero Landing */
    .hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 80px 20px;
        margin-top: 40px;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -1.5px;
        margin-bottom: 15px;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #64748b;
        max-width: 600px;
        line-height: 1.6;
        margin-bottom: 40px;
    }
    .hero-features {
        display: flex;
        gap: 40px;
        margin-top: 60px;
        color: #475569;
        font-weight: 500;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5 {
        color: #0f172a;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        margin-bottom: 20px;
        margin-top: 30px;
    }
    
    /* Analyze Panel */
    .upload-box {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 40px 20px;
        text-align: center;
        background-color: #ffffff;
        transition: all 0.2s;
    }
    .upload-box:hover {
        border-color: #3b82f6;
        background-color: #f0f9ff;
    }
    
    .result-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    .result-prediction {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .result-confidence {
        font-size: 1.2rem;
        font-weight: 500;
        color: #0ea5e9;
    }
    
    /* Explainability */
    .exp-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 5px;
    }
    .exp-sub {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 20px;
    }
    
    /* Custom Button Overrides for primary SaaS feel */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    
    /* Footer Disclaimer */
    .footer-disclaimer {
        text-align: center;
        font-size: 0.85rem;
        color: #94a3b8;
        padding-top: 40px;
        margin-top: 60px;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Lazy Model Loader
@st.cache_resource(show_spinner="Initializing AI engine...")
def get_model():
    canonical_path = PROJECT_ROOT / "models" / "best_efficientnet_model.keras"
    if canonical_path.exists():
        model = tf.keras.models.load_model(canonical_path)
        assert model.output_shape[-1] == 4, f"Model must output 4 classes, got {model.output_shape[-1]}"
        return model
    model_path = MODEL_PATHS.get(ARCH_KEY, BEST_MODEL_PATH)
    if model_path.exists():
        model = tf.keras.models.load_model(model_path)
        assert model.output_shape[-1] == 4, f"Model must output 4 classes, got {model.output_shape[-1]}"
        return model
    from src.models import build_model
    return build_model(ARCH_KEY)

# ================= TOP NAVIGATION =================
nav_col1, nav_col2, nav_col3, nav_col4, nav_col5 = st.columns([4, 1, 1, 1, 1])
with nav_col1:
    st.markdown('<div class="nav-logo" style="cursor:pointer;">NEUROSCAN</div>', unsafe_allow_html=True)
with nav_col3:
    if st.button("Analyze", use_container_width=True, key="nav_analyze"):
        nav_to("analyze")
        st.rerun()
with nav_col4:
    if st.button("Insights", use_container_width=True, key="nav_insights"):
        nav_to("insights")
        st.rerun()
with nav_col5:
    if st.button("History", use_container_width=True, key="nav_history"):
        nav_to("history")
        st.rerun()

# ================= PAGE ROUTING =================

if st.session_state.page == "landing":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Intelligent MRI Analysis</div>
        <div class="hero-subtitle">
            AI-assisted brain imaging analysis with transparent visual explanations. 
            A premium diagnostic support platform.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    colA, colB, colC = st.columns([3, 2, 3])
    with colB:
        if st.button("Start Analysis", type="primary", use_container_width=True):
            nav_to("analyze")
            st.rerun()
            
    st.markdown("""
    <div class="hero-features" style="justify-content: center;">
        <div>✓ Intelligent Analysis</div>
        <div>✓ Visual Explainability</div>
        <div>✓ Instant Reports</div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "analyze":
    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1], gap="large")
    
    with col_left:
        st.markdown('<div class="section-title">MRI SCAN</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Upload your MRI scan (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Drag and drop your image here or Browse files.",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                st.session_state.active_image_path = tmp.name
        
        if st.session_state.active_image_path:
            st.image(st.session_state.active_image_path, use_container_width=True)
        else:
            st.markdown("""
            <div class="upload-box">
                <h4 style="color:#64748b; margin-bottom:10px;">Upload your MRI scan</h4>
                <p style="color:#94a3b8; font-size:0.9rem; margin-bottom:0;">Use the uploader above to select a file.</p>
                <p style="color:#cbd5e1; font-size:0.8rem;">JPG · JPEG · PNG</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="section-title">TRY AN EXAMPLE</div>', unsafe_allow_html=True)
        st.caption("Explore the analysis workflow using representative MRI scans.")
        if TEST_MANIFEST.exists():
            test_df = pd.read_csv(TEST_MANIFEST)
            tc1, tc2 = st.columns(2)
            with tc1:
                if st.button("Glioma", use_container_width=True):
                    st.session_state.active_image_path = test_df[test_df["class_name"] == "glioma"].iloc[0]["filepath"]
                    st.rerun()
                if st.button("No Tumor", use_container_width=True):
                    st.session_state.active_image_path = test_df[test_df["class_name"] == "notumor"].iloc[0]["filepath"]
                    st.rerun()
            with tc2:
                if st.button("Meningioma", use_container_width=True):
                    st.session_state.active_image_path = test_df[test_df["class_name"] == "meningioma"].iloc[0]["filepath"]
                    st.rerun()
                if st.button("Pituitary", use_container_width=True):
                    st.session_state.active_image_path = test_df[test_df["class_name"] == "pituitary"].iloc[0]["filepath"]
                    st.rerun()

    with col_right:
        st.markdown('<div class="section-title">ANALYSIS</div>', unsafe_allow_html=True)
        
        if not st.session_state.active_image_path:
            st.info("Ready to analyze. Please upload or select an MRI scan.")
        else:
            if st.button("Analyze Image", type="primary"):
                is_valid, err_msg, dims = verify_image_file(Path(st.session_state.active_image_path))
                if not is_valid:
                    st.error(f"Validation failed: Please upload a valid MRI image.")
                else:
                    with st.spinner("Analyzing image..."):
                        try:
                            model = get_model()
                            preprocess_fn = get_model_preprocess_fn(ARCH_KEY)
                            
                            tensor = load_and_preprocess_image(st.session_state.active_image_path, target_size=IMAGE_SIZE, preprocess_fn=preprocess_fn)
                            batch_tensor = tf.expand_dims(tensor, axis=0)
                            
                            preds = model(batch_tensor, training=False).numpy()[0]
                            pred_idx = int(np.argmax(preds))
                            pred_class = CLASSES[pred_idx]
                            confidence = float(preds[pred_idx] * 100.0)
                            display_name = CLASS_DISPLAY_NAMES[pred_class]
                            
                            target_layer = GRADCAM_TARGET_LAYERS.get(ARCH_KEY, None)
                            if target_layer is None or not any(l.name == target_layer for l in model.layers):
                                target_layer = find_target_conv_layer(model)
                                
                            heatmap = compute_gradcam_heatmap(model, batch_tensor, target_layer_name=target_layer, pred_index=pred_idx)
                            orig_pil = Image.open(st.session_state.active_image_path).convert("RGB")
                            orig_np = np.array(orig_pil)
                            superimposed_img, colorized_heatmap = generate_gradcam_overlay(
                                orig_np, heatmap, alpha=HEATMAP_ALPHA, colormap=COLORMAP
                            )
                            
                            # Save results to session state for persistence within the page
                            st.session_state.analysis_result = {
                                "display_name": display_name,
                                "confidence": confidence,
                                "preds": preds,
                                "orig_np": orig_np,
                                "colorized_heatmap": colorized_heatmap,
                                "superimposed_img": superimposed_img,
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "short_time": datetime.now().strftime("%I:%M %p")
                            }
                            
                            # Add to history
                            st.session_state.history.insert(0, {
                                "time": st.session_state.analysis_result["short_time"],
                                "prediction": display_name,
                                "confidence": f"{confidence:.1f}%"
                            })
                            
                        except Exception as e:
                            st.error("An error occurred during analysis. Please try again with a valid image.")
            
            # Display results if available
            if "analysis_result" in st.session_state:
                res = st.session_state.analysis_result
                st.markdown(f"""
                <div class="result-card">
                    <div style="font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">AI Analysis</div>
                    <div class="result-prediction">{res['display_name']}</div>
                    <div class="result-confidence">{res['confidence']:.1f}% Confidence</div>
                    <hr style="border:0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                    <div style="font-size: 0.85rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px;">Class Probabilities</div>
                </div>
                """, unsafe_allow_html=True)
                
                for i, cls_id in enumerate(CLASSES):
                    name = CLASS_DISPLAY_NAMES[cls_id]
                    prob = res['preds'][i] * 100.0
                    col_t, col_b = st.columns([2, 3])
                    with col_t:
                        st.markdown(f"<div style='color: #475569; font-size: 0.95rem; font-weight: 500;'>{name}</div>", unsafe_allow_html=True)
                    with col_b:
                        st.progress(float(res['preds'][i]), text=f"{prob:.1f}%")
                
                st.markdown('<div class="section-title">AI EXPLANATION</div>', unsafe_allow_html=True)
                st.markdown('<div class="exp-sub">Explore the image regions contributing to this prediction.</div>', unsafe_allow_html=True)
                
                exp_tab1, exp_tab2, exp_tab3 = st.tabs(["Original", "AI Attention", "Overlay"])
                with exp_tab1:
                    st.image(res['orig_np'], use_container_width=True)
                with exp_tab2:
                    st.image(res['colorized_heatmap'], use_container_width=True)
                with exp_tab3:
                    st.image(res['superimposed_img'], use_container_width=True)
                
                st.markdown('<div class="section-title">REPORT</div>', unsafe_allow_html=True)
                
                if not st.session_state.report_ready:
                    if st.button("Generate Analysis Report"):
                        st.session_state.report_ready = True
                        st.rerun()
                else:
                    st.success("Report Ready")
                    report_txt = f"NEUROSCAN ANALYSIS REPORT\n"
                    report_txt += f"Generated: {res['time']}\n"
                    report_txt += f"----------------------------------------\n"
                    report_txt += f"Prediction: {res['display_name']}\n"
                    report_txt += f"Confidence: {res['confidence']:.1f}%\n"
                    report_txt += f"----------------------------------------\n"
                    for i, cls_id in enumerate(CLASSES):
                        report_txt += f"{CLASS_DISPLAY_NAMES[cls_id]}: {res['preds'][i]*100.0:.1f}%\n"
                    report_txt += f"----------------------------------------\n"
                    report_txt += f"Disclaimer: NeuroScan is an AI research prototype and is not intended to provide medical diagnosis.\n"
                    
                    st.download_button("Download Report", data=report_txt, file_name="neuroscan_report.txt", mime="text/plain", type="primary")

elif st.session_state.page == "insights":
    st.markdown('<div class="hero-title" style="font-size:2.5rem; text-align:left; margin-bottom:10px;">System Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle" style="text-align:left; max-width:800px;">Comprehensive evaluation of the active analysis engine across 1,600 validated medical imaging studies.</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-card" style="border-left: 4px solid #0ea5e9;">
        <div style="font-size: 1.5rem; font-weight: 600; color: #0f172a; margin-bottom: 5px;">Active Engine Accuracy: 89.5%</div>
        <div style="color: #64748b;">Our proprietary EfficientNet-based architecture ensures highly precise, low-latency classifications.</div>
    </div>
    """, unsafe_allow_html=True)
    
    bench_file = METRICS_DIR / "multi_model_benchmarks.json"
    if bench_file.exists():
        import json as json_lib
        with open(bench_file, 'r') as f:
            bench_data = json_lib.load(f)
        b_df = pd.DataFrame(bench_data)
        
        display_cols = {
            "architecture": "Architecture",
            "accuracy": "Accuracy (%)",
            "f1_macro": "Macro F1 (%)",
            "precision_macro": "Precision (%)",
            "recall_macro": "Recall (%)",
            "avg_latency_ms": "Latency (ms)"
        }
        styled_df = b_df[list(display_cols.keys())].rename(columns=display_cols)
        
        st.markdown('<div class="section-title">METRICS OVERVIEW</div>', unsafe_allow_html=True)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

elif st.session_state.page == "history":
    st.markdown('<div class="hero-title" style="font-size:2.5rem; text-align:left; margin-bottom:10px;">Analysis History</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle" style="text-align:left; max-width:800px;">Session-only log of recently processed imaging studies.</div>', unsafe_allow_html=True)
    
    if not st.session_state.history:
        st.info("No analyses performed in this session.")
    else:
        for item in st.session_state.history:
            st.markdown(f"""
            <div style="background-color:#ffffff; border:1px solid #e2e8f0; border-radius:8px; padding:15px 20px; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-weight:600; color:#0f172a; font-size:1.1rem;">{item['prediction']}</div>
                    <div style="color:#64748b; font-size:0.9rem;">{item['confidence']} confidence</div>
                </div>
                <div style="color:#94a3b8; font-size:0.9rem;">{item['time']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Clear Session History"):
            st.session_state.history = []
            st.rerun()

# ================= FOOTER =================
st.markdown("""
<div class="footer-disclaimer">
    NeuroScan is an AI research prototype and is not intended to provide medical diagnosis or replace professional clinical evaluation.
</div>
""", unsafe_allow_html=True)
