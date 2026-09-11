from datetime import datetime
from fastapi import APIRouter
from backend.schemas.analysis import ReportRequest, ReportResponse

router = APIRouter(prefix="/api", tags=["report"])

@router.post("/report", response_model=ReportResponse)
def generate_report(req: ReportRequest):
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    report_lines = [
        "================================================================================",
        "                         NEUROSCAN AI — CLINICAL STUDY REPORT",
        "================================================================================",
        f"Analysis Reference ID : {req.analysis_id}",
        f"Generated Timestamp   : {now_str}",
        "Modality              : Brain Magnetic Resonance Imaging (MRI)",
        "Classification Engine : EfficientNet-B0 (Transfer Learning Pretrained)",
        "--------------------------------------------------------------------------------",
        "FINDINGS SUMMARY:",
        f"Primary Prediction    : {req.prediction}",
        f"Model Confidence      : {req.confidence * 100:.1f}%",
        "--------------------------------------------------------------------------------",
        "CLASS PROBABILITY DISTRIBUTION:",
    ]
    
    for cls_name, prob in req.probabilities.items():
        bar_len = int(prob * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        report_lines.append(f"  - {cls_name:<20} : {prob*100:5.1f}%  [{bar}]")
        
    report_lines.extend([
        "--------------------------------------------------------------------------------",
        "EXPLAINABLE AI (GRAD-CAM) INTERPRETABILITY:",
        "  - Visual activation analysis conducted across feature layer 'top_conv'.",
        "  - Activation maps highlight focused focal anatomical structures relevant to",
        "    the indicated class prediction.",
        "--------------------------------------------------------------------------------",
        "RESPONSIBLE AI & MEDICAL DISCLAIMER:",
        "  NeuroScan AI is an academic/research prototype for brain MRI classification.",
        "  It is not a certified medical device and must NOT be used as a sole basis for",
        "  clinical diagnosis or patient treatment. Interpretation must be verified by a",
        "  board-certified radiologist or qualified physician.",
        "================================================================================",
    ])

    report_text = "\n".join(report_lines)

    return ReportResponse(
        analysis_id=req.analysis_id,
        report_text=report_text,
        generated_at=now_str
    )
