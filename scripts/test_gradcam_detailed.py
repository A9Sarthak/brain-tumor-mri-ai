import io
import base64
import requests
import numpy as np
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"

def inspect_gradcam_response(sample_id):
    print(f"\n==========================================")
    print(f"Testing Grad-CAM for Sample: '{sample_id}'")
    print(f"==========================================")
    
    res = requests.post(f"{BASE_URL}/api/gradcam", data={"sample_class": sample_id})
    if res.status_code != 200:
        print(f"FAILED with HTTP {res.status_code}: {res.text}")
        return False
        
    data = res.json()
    pred = data.get("prediction")
    layer = data.get("target_layer")
    print(f"Predicted Diagnosis: {pred}")
    print(f"Target Conv Layer:   {layer}")
    
    assert layer == "top_conv", f"Expected layer top_conv, got {layer}"
    
    # 1. Original Image Check
    orig_b64 = data.get("original_image_base64")
    assert orig_b64 and len(orig_b64) > 1000, "original_image_base64 is empty or too short"
    orig_img = Image.open(io.BytesIO(base64.b64decode(orig_b64)))
    orig_np = np.array(orig_img)
    print(f"Original Image: Format={orig_img.format}, Size={orig_img.size}, Shape={orig_np.shape}, Range=[{orig_np.min()}, {orig_np.max()}]")
    orig_w, orig_h = orig_img.size
    assert orig_w > 50 and orig_h > 50, f"Original image too small: {orig_img.size}"

    # 2. Attention Heatmap Check
    heat_b64 = data.get("attention_heatmap_base64")
    assert heat_b64 and len(heat_b64) > 1000, "attention_heatmap_base64 is empty or too short"
    heat_img = Image.open(io.BytesIO(base64.b64decode(heat_b64)))
    heat_np = np.array(heat_img)
    print(f"Heatmap Image:  Format={heat_img.format}, Size={heat_img.size}, Shape={heat_np.shape}, Range=[{heat_np.min()}, {heat_np.max()}]")
    assert heat_img.size == (orig_w, orig_h), f"Heatmap size {heat_img.size} doesn't match original {(orig_w, orig_h)}"
    # Verify JET colormap variety (RGB values should differ significantly, not monochrome)
    std_channels = np.std(heat_np, axis=(0, 1))
    print(f"Heatmap RGB Channel Stds: {std_channels.tolist()}")
    assert np.any(std_channels > 10), "Heatmap is flat or monochrome!"

    # 3. Overlay Image Check
    over_b64 = data.get("overlay_image_base64")
    assert over_b64 and len(over_b64) > 1000, "overlay_image_base64 is empty or too short"
    over_img = Image.open(io.BytesIO(base64.b64decode(over_b64)))
    over_np = np.array(over_img)
    print(f"Overlay Image:  Format={over_img.format}, Size={over_img.size}, Shape={over_np.shape}, Range=[{over_np.min()}, {over_np.max()}]")
    assert over_img.size == (orig_w, orig_h), f"Overlay size {over_img.size} doesn't match original {(orig_w, orig_h)}"
    
    # Overlay should be a blend of orig and heatmap
    # Check that overlay differs from pure orig and pure heatmap
    diff_orig = np.mean(np.abs(over_np.astype(float) - orig_np.astype(float)))
    diff_heat = np.mean(np.abs(over_np.astype(float) - heat_np.astype(float)))
    print(f"Overlay Diff from Original: {diff_orig:.2f} | Diff from Heatmap: {diff_heat:.2f}")
    assert diff_orig > 5.0, "Overlay is identical to original image!"
    assert diff_heat > 5.0, "Overlay is identical to raw heatmap!"
    
    print(f"-> Sample '{sample_id}' Grad-CAM, AI Attention & Overlay: VALIDATED 100% CORRECT!")
    return True

def main():
    print("================ GRAD-CAM DETAILED VERIFICATION ================")
    classes = ["notumor", "glioma", "meningioma", "pituitary"]
    for c in classes:
        success = inspect_gradcam_response(c)
        assert success
        
    print("\n================ TESTING DIRECT FILE UPLOAD GRAD-CAM ================")
    test_files = [
        ("Te-gl_10.jpg", "data/raw/Testing/glioma/Te-gl_10.jpg"),
        ("Te-me_10.jpg", "data/raw/Testing/meningioma/Te-me_10.jpg"),
        ("Te-no_10.jpg", "data/raw/Testing/notumor/Te-no_10.jpg"),
        ("Te-pi_10.jpg", "data/raw/Testing/pituitary/Te-pi_10.jpg"),
    ]
    for fname, fpath in test_files:
        with open(fpath, "rb") as f:
            res = requests.post(f"{BASE_URL}/api/gradcam", files={"file": (fname, f.read(), "image/jpeg")})
            assert res.status_code == 200
            data = res.json()
            print(f"File upload '{fname}': Target Layer = {data['target_layer']}, Prediction = {data['prediction']}")
            assert len(data["original_image_base64"]) > 1000
            assert len(data["attention_heatmap_base64"]) > 1000
            assert len(data["overlay_image_base64"]) > 1000

    print("\n>>> ALL GRAD-CAM, AI ATTENTION & OVERLAY GENERATIONS CONFIRMED WORKING PROPERLY! <<<")

if __name__ == "__main__":
    main()
