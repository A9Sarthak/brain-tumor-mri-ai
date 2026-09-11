"""
Phase 2 Unit Tests: Multi-Model Architecture Builders, Grad-CAM Explainability, and Benchmarks.
"""
import sys
from pathlib import Path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
import numpy as np
import tensorflow as tf

from src.config import (
    CLASSES,
    NUM_CLASSES,
    INPUT_SHAPE,
    IMAGE_SIZE,
    METRICS_DIR,
    PLOTS_DIR,
)
from src.models import (
    build_resnet50_model,
    build_efficientnet_model,
    build_mobilenet_model,
    build_vgg16_model,
    build_model,
)
from src.gradcam import (
    compute_gradcam_heatmap,
    generate_gradcam_overlay,
    analyze_activation_focus,
    find_target_conv_layer,
)
from src.utils import load_json


class TestMultiModelArchitectures:
    """Validate construction and properties of all 4 CNN transfer learning architectures."""

    def test_resnet50_builder(self):
        model = build_resnet50_model()
        assert model.output_shape == (None, NUM_CLASSES)
        assert model.input_shape == (None, 224, 224, 3)
        assert model.loss == "sparse_categorical_crossentropy"

    def test_factory_dispatcher_all_architectures(self):
        for arch in ["ResNet50", "EfficientNet-B0", "MobileNetV2"]:
            m = build_model(arch)
            assert m.output_shape == (None, NUM_CLASSES)
            assert m.count_params() > 1_000_000

    def test_invalid_architecture_raises_error(self):
        with pytest.raises(ValueError, match="Unknown architecture"):
            build_model("NonExistentCNN")


class TestGradCAMExplainability:
    """Validate Grad-CAM heatmap generation, overlays, and focus calculations."""

    @pytest.fixture
    def sample_model_and_input(self):
        model = build_resnet50_model()
        dummy_input = tf.random.uniform((1, 224, 224, 3), minval=-1.0, maxval=1.0)
        return model, dummy_input

    def test_target_conv_layer_identification(self, sample_model_and_input):
        model, _ = sample_model_and_input
        target = find_target_conv_layer(model, preferred_name="conv5_block3_out")
        assert target == "conv5_block3_out"

    def test_gradcam_heatmap_computation(self, sample_model_and_input):
        model, dummy_input = sample_model_and_input
        heatmap = compute_gradcam_heatmap(model, dummy_input, target_layer_name="conv5_block3_out")
        assert isinstance(heatmap, np.ndarray)
        assert heatmap.ndim == 2
        assert np.min(heatmap) >= 0.0
        assert np.max(heatmap) <= 1.0

    def test_gradcam_overlay_dimensions_and_types(self):
        dummy_orig = np.zeros((224, 224, 3), dtype=np.uint8)
        dummy_heatmap = np.random.uniform(0.0, 1.0, (7, 7)).astype(np.float32)
        superimposed, colorized = generate_gradcam_overlay(dummy_orig, dummy_heatmap)
        assert superimposed.shape == (224, 224, 3)
        assert superimposed.dtype == np.uint8
        assert colorized.shape == (224, 224, 3)

    def test_activation_focus_analysis(self):
        dummy_heatmap = np.zeros((10, 10), dtype=np.float32)
        dummy_heatmap[5, 5] = 1.0
        dummy_heatmap[5, 6] = 0.8
        focus = analyze_activation_focus(dummy_heatmap)
        assert "anatomical_region" in focus
        assert "focus_intensity_pct" in focus
        assert focus["focus_intensity_pct"] == 100.0


class TestBenchmarkingConsistency:
    """Validate benchmark metrics file structure and chart generation."""

    def test_benchmark_json_exists_and_valid(self):
        bench_file = METRICS_DIR / "multi_model_benchmarks.json"
        assert bench_file.exists(), "multi_model_benchmarks.json must exist"
        data = load_json(bench_file)
        assert len(data) == 4
        architectures = [d["architecture"] for d in data]
        assert "ResNet50" in architectures
        assert "EfficientNet-B0" in architectures
        assert "MobileNetV2" in architectures
        assert "VGG16" in architectures

    def test_benchmark_charts_exist(self):
        chart1 = PLOTS_DIR / "multi_model_accuracy_f1.png"
        chart2 = PLOTS_DIR / "latency_vs_accuracy.png"
        assert chart1.exists(), "multi_model_accuracy_f1.png must exist"
        assert chart2.exists(), "latency_vs_accuracy.png must exist"
