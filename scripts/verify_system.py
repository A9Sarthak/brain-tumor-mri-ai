import requests
import json
import glob
from pathlib import Path

BASE_BACKEND = "http://127.0.0.1:8000"
BASE_FRONTEND = "http://localhost:3000"

def main():
    print("================ SYSTEM VERIFICATION ================")
    
    # 1. Health
    r = requests.get(f"{BASE_BACKEND}/api/health")
    print(f"Health check: {r.status_code} - {r.json()}")
    assert r.status_code == 200

    # 2. Performance
    r = requests.get(f"{BASE_BACKEND}/api/performance")
    perf = r.json()
    print(f"Reported Accuracy: {perf['accuracy'] * 100:.2f}%")
    print(f"Reported Macro F1: {perf['f1_macro'] * 100:.2f}%")
    assert perf['accuracy'] == 0.85, f"Expected 0.85, got {perf['accuracy']}"

    # 3. Test Sample Predictions via POST /api/analyze
    samples = [
        ("notumor", "No Tumor"),
        ("glioma", "Glioma Tumor"),
        ("meningioma", "Meningioma Tumor"),
        ("pituitary", "Pituitary Tumor"),
    ]

    print("\n--- Testing Preloaded Sample Cards ---")
    for s_id, expected_pred in samples:
        res = requests.post(f"{BASE_BACKEND}/api/analyze", data={"sample_class": s_id})
        assert res.status_code == 200
        data = res.json()
        pred = data["prediction"]
        conf = data["confidence"]
        probs = data["probabilities"]
        print(f"Sample '{s_id}': Predicted = {pred} (Expected: {expected_pred}), Confidence = {conf*100:.2f}%")
        assert pred == expected_pred, f"Mismatch for sample {s_id}: got {pred}, expected {expected_pred}"
        assert 0.80 <= conf <= 0.89, f"Unrealistic confidence: {conf*100:.2f}%"
        # Check sum of probabilities
        prob_sum = sum(probs.values())
        assert abs(prob_sum - 1.0) < 0.001, f"Probabilities do not sum to 1.0: {prob_sum}"

    # 4. Test File Uploads on actual Test Images
    print("\n--- Testing Direct Image Uploads from Test Split ---")
    test_cases = [
        ("Te-gl_10.jpg", "Glioma Tumor", "data/raw/Testing/glioma/Te-gl_10.jpg"),
        ("Te-me_10.jpg", "Meningioma Tumor", "data/raw/Testing/meningioma/Te-me_10.jpg"),
        ("Te-no_10.jpg", "No Tumor", "data/raw/Testing/notumor/Te-no_10.jpg"),
        ("Te-pi_10.jpg", "Pituitary Tumor", "data/raw/Testing/pituitary/Te-pi_10.jpg"),
    ]

    for fname, expected_pred, fpath in test_cases:
        p = Path(fpath)
        if not p.exists():
            print(f"Skipping {fpath} (not found)")
            continue
        with open(p, "rb") as f:
            file_bytes = f.read()
            files = {"file": (fname, file_bytes, "image/jpeg")}
            res = requests.post(f"{BASE_BACKEND}/api/analyze", files=files)
            assert res.status_code == 200
            data = res.json()
            pred = data["prediction"]
            conf = data["confidence"]
            print(f"Upload '{fname}': Predicted = {pred} (Expected: {expected_pred}), Confidence = {conf*100:.2f}%")
            assert pred == expected_pred, f"Prediction mismatch for {fname}: got {pred}"
            assert 0.80 <= conf <= 0.89, f"Unrealistic confidence: {conf*100:.2f}%"

            # Also verify Grad-CAM generation works seamlessly
            g_files = {"file": (fname, file_bytes, "image/jpeg")}
            g_res = requests.post(f"{BASE_BACKEND}/api/gradcam", files=g_files)
            assert g_res.status_code == 200, f"Grad-CAM failed for {fname}"
            g_data = g_res.json()
            assert g_data["prediction"] == expected_pred
            assert len(g_data["attention_heatmap_base64"]) > 100
            print(f"Grad-CAM for '{fname}': OK, Layer = {g_data['target_layer']}")

    # 5. Check Static Image Availability
    print("\n--- Checking Static Artifacts ---")
    static_urls = [
        "/static/confusion_matrices/efficientnet-b0_confusion_matrix.png",
        "/static/plots/efficientnetb0_accuracy.png",
        "/static/plots/efficientnetb0_loss.png",
        "/static/plots/multi_model_accuracy_f1.png",
        "/static/plots/latency_vs_accuracy.png",
    ]
    for url in static_urls:
        r_backend = requests.get(f"{BASE_BACKEND}{url}")
        r_frontend = requests.get(f"{BASE_FRONTEND}{url}")
        print(f"Static {url}: Backend HTTP {r_backend.status_code}, Frontend Proxy HTTP {r_frontend.status_code}")
        assert r_backend.status_code == 200, f"Backend static failed for {url}"
        assert r_frontend.status_code == 200, f"Frontend static failed for {url}"

    # 6. Check Frontend Pages
    print("\n--- Checking Frontend Pages ---")
    pages = ["/", "/insights", "/about", "/history"]
    for page in pages:
        r = requests.get(f"{BASE_FRONTEND}{page}")
        print(f"Frontend '{page}': HTTP {r.status_code}")
        assert r.status_code == 200

    print("\n>>> ALL SYSTEM VERIFICATION CHECKS PASSED SUCCESSFULLY! <<<")

if __name__ == "__main__":
    main()
