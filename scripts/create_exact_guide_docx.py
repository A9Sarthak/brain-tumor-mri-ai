"""
Generate Word document matching the exact requested text:
NeuroCausal_X_Architectural_Guide.docx
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tc_pr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tc_mar.append(node)
    tc_pr.append(tc_mar)

def create_guide_doc():
    doc = Document()

    # Set 1-inch margins
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # Styles
    styles = doc.styles
    normal_style = styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59) # Slate 800

    NAVY = RGBColor(15, 23, 42)      # #0F172A
    DARK_BLUE = RGBColor(30, 58, 138) # #1E3A8A
    TEAL = RGBColor(13, 148, 136)    # #0D9488
    SLATE = RGBColor(71, 85, 105)    # #475569

    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("NeuroCausal-X™: Comprehensive In-Depth Architectural Guide")
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = NAVY

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(14)
    r_sub = p_sub.add_run("SOTA Causal Inpainting Ablation, Conformal Uncertainty Sets & Radiomic Morphometry")
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = TEAL

    # Horizontal divider line via paragraph border or spacing
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)

    # Helper functions
    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(14.5)
        r.font.color.rgb = DARK_BLUE
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(12.5)
        r.font.color.rgb = TEAL
        return h

    def add_h3(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
        r = h.add_run(text)
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = NAVY
        return h

    def add_callout(quote_text, speaker=""):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, 90, 90, 130, 130)
        p = cell.paragraphs[0]
        if speaker:
            r_sp = p.add_run(speaker + "\n")
            r_sp.bold = True
            r_sp.font.size = Pt(10)
            r_sp.font.color.rgb = DARK_BLUE
        r_q = p.add_run(quote_text)
        r_q.font.size = Pt(10)
        r_q.font.italic = True
        r_q.font.color.rgb = SLATE
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_code_block(text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, "0F172A") # Dark background
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.name = 'Consolas'
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(241, 245, 249) # Light text
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # -----------------------------------------------------------------
    # SECTION 1
    # -----------------------------------------------------------------
    add_h1("1. The Big Picture: Plain-English Analogy")

    p = doc.add_paragraph()
    p.add_run("Imagine you are in a hospital with two different junior doctors reviewing your brain MRI:")

    p_docA = doc.add_paragraph()
    p_docA.paragraph_format.left_indent = Inches(0.25)
    r1 = p_docA.add_run("• Doctor A (Standard AI / What 99% of GitHub projects do):\n")
    r1.bold = True
    r1.font.color.rgb = DARK_BLUE
    p_docA.add_run(
        'Doctor A glances at the scan, pulls a number out of thin air, and says: '
        '"I am 98% confident you have a Meningioma."\n'
        'When you ask why, they hand you a blurry thermal heatmap with a red blob on it. '
        'When you ask: "What if that red blob is just an artifact from the scanner?" or '
        '"Could it be a Glioma instead?", Doctor A has no answer. They cannot prove causality, and they cannot give you a safety margin.'
    )

    p_docB = doc.add_paragraph()
    p_docB.paragraph_format.left_indent = Inches(0.25)
    p_docB.paragraph_format.space_after = Pt(10)
    r2 = p_docB.add_run("• Doctor B (NeuroCausal-X™):\n")
    r2.bold = True
    r2.font.color.rgb = TEAL
    p_docB.add_run(
        'Doctor B reviews the scan and says:\n'
        '1. "Statistically, with a 95% mathematical guarantee, the true diagnosis lies within the differential set: {Glioma, Meningioma}. '
        'There is borderline tissue ambiguity, so I am not going to gamble with a single guess."\n'
        '2. "To prove the AI isn\'t hallucinating on scanner noise, I performed a digital lesion resection: I digitally erased the tumor using the healthy side of your brain as a template. '
        'When the tumor vanished, the AI\'s tumor confidence collapsed from 86% down to 8% (ΔP = 78%). That proves the diagnosis is causally driven by the lesion, not image artifacts."\n'
        '3. "Here are the exact physical measurements: the cross-sectional area is 342 mm², the sphericity index is 0.72 (indicating a smooth, circumscribed boundary), '
        'and its position sits on the extra-axial dural border, which heavily supports Meningioma over an infiltrative Glioma."'
    )

    p_summary = doc.add_paragraph()
    r_sum = p_summary.add_run("NeuroCausal-X™ transforms this project from a black-box guessing tool into a publication-grade clinical decision engine.")
    r_sum.bold = True
    r_sum.font.color.rgb = DARK_BLUE

    # -----------------------------------------------------------------
    # SECTION 2
    # -----------------------------------------------------------------
    add_h1("2. What Was the Research Gap Before? (The 3 Fatal Flaws of Standard Projects)")

    p = doc.add_paragraph()
    p.add_run(
        "Almost every brain tumor detection project published by students or on Kaggle/GitHub makes three fundamental scientific mistakes:"
    )

    gap_table = doc.add_table(rows=4, cols=3)
    gap_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    gap_table.autofit = False

    t_headers = ["The Flaw", "What Standard Projects Do", "Why It Fails Clinically"]
    for i, h_text in enumerate(t_headers):
        cell = gap_table.cell(0, i)
        set_cell_background(cell, "0F172A")
        p = cell.paragraphs[0]
        r = p.add_run(h_text)
        r.bold = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(255, 255, 255)

    gaps_content = [
        (
            "1. The \"Softmax Lie\"\n(Uncalibrated Confidence)",
            "Take raw softmax outputs (e.g. 96%) and treat them as true probabilities. If forced, they clamp it with hacks.",
            "Softmax is notoriously overconfident. It guesses 90%+ even on ambiguous scans."
        ),
        (
            "2. The \"Saliency Illusion\"\n(Clever Hans Effect)",
            "Display a standard Grad-CAM heatmap (a soft red/yellow blob).",
            "Heatmaps show correlation, NOT causation (the \"Clever Hans\" shortcut learning bug)."
        ),
        (
            "3. The \"Radiologist Disconnect\"\n(Zero Morphometry)",
            "Output only a label: \"Meningioma\". No physical dimensions, borders, or anatomical compartments provided.",
            "Radiologists never diagnose without area (mm²), border roughness, and cranial locus."
        )
    ]

    widths = [Inches(2.0), Inches(2.2), Inches(2.3)]
    for r_idx, (c0_text, c1_text, c2_text) in enumerate(gaps_content, start=1):
        row = gap_table.rows[r_idx]
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, text in enumerate([c0_text, c1_text, c2_text]):
            cell = row.cells[c_idx]
            cell.width = widths[c_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 100, 100)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(9.5)
            r.font.color.rgb = NAVY

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -----------------------------------------------------------------
    # SECTION 3
    # -----------------------------------------------------------------
    add_h1("3. How NeuroCausal-X™ Solves Each Gap Step-by-Step")

    add_h2("Pillar 1: Split Conformal Prediction Sets (P(Y in Ĉ) >= 95%)")
    add_h3("The Clinical Problem")
    p = doc.add_paragraph()
    p.add_run(
        "Deep learning models are notoriously overconfident. A standard CNN might predict:\n"
        "Glioma: 52%, Meningioma: 44%, Pituitary: 3%, No Tumor: 1%\n"
        "In a typical app, the code simply takes argmax, forces a single diagnosis (\"Glioma Tumor: 52%\"), "
        "and hides the fact that it was essentially a coin toss. In clinical medicine, a forced single guess on a borderline scan leads to misdiagnosis and inappropriate surgical planning."
    )

    add_h3("What We Implemented")
    p = doc.add_paragraph()
    p.add_run(
        "We implemented Inductive Split Conformal Prediction (based on Angelopoulos & Bates, 2023 and CONSeg, 2024–2025). "
        "Conformal prediction is a branch of modern statistics that provides distribution-free, finite-sample statistical coverage guarantees:\n"
    )
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq1 = p_eq1.add_run("P( Y_true ∈ Ĉ_{1-α}(X) ) ≥ 1 - α")
    r_eq1.bold = True
    r_eq1.font.size = Pt(12)
    r_eq1.font.color.rgb = DARK_BLUE

    add_h3("How It Works Step-by-Step:")
    steps_p1 = [
        ("1. Calibration Phase: ", "On a held-out calibration dataset, we calculate the model's non-conformity score for every sample: s_i = 1 - f(X_i)_{y_i} (where f(X_i)_{y_i} is the probability assigned to the true label y_i)."),
        ("2. Quantile Threshold: ", "We compute the critical (1 - α) empirical quantile threshold q̂_α (for α = 0.05 ⟹ 95% confidence guarantee, threshold ≈ 0.082)."),
        ("3. Set Generation: ", "For any newly uploaded scan, instead of outputting one class, the engine includes every class whose calibrated probability meets the threshold:\nĈ_{0.95}(X) = { c ∈ Y : P(Y = c | X) ≥ 1 - q̂_{0.05} }"),
        ("4. Ambiguity Categorization: ", "\n• Singleton Set (|Ĉ| = 1): e.g., {\"Pituitary Tumor\"}. The AI is statistically confident that no other class is plausible.\n• Bimodal Differential (|Ĉ| = 2): e.g., {\"Glioma Tumor\", \"Meningioma Tumor\"}. The AI alerts the clinician: \"Tissue characteristics overlap. A differential radiologist review between Glioma and Meningioma is required.\""),
        ("5. Shannon Entropy & Epistemic Uncertainty: ", "We compute the information entropy of the probability vector:\nH(p) = -∑ p_i * ln(p_i)\nNormalized against maximum theoretical entropy ln(4) ≈ 1.3863, generating an Epistemic Uncertainty Gauge (0% to 100%).")
    ]
    for stitle, sdesc in steps_p1:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        r_t = p.add_run(stitle)
        r_t.bold = True
        r_t.font.color.rgb = DARK_BLUE
        p.add_run(sdesc)

    # Pillar 2
    add_h2("Pillar 2: Counterfactual Digital Lesion Resection & Causal Attribution (ΔP)")
    add_h3("The Clinical Problem: The \"Clever Hans\" Effect")
    p = doc.add_paragraph()
    p.add_run(
        "In 1904, a horse named Clever Hans was believed to solve math problems by tapping his hoof. In reality, the horse was simply watching the unconscious facial cues of his trainer.\n"
        "In medical computer vision, deep neural networks often suffer from this exact same failure: a model might predict \"Glioma\" not because it analyzed the tumor cells, but because of spurious correlations (e.g., patient positioning, skull bone density, or slice contrast markers).\n"
        "Standard Grad-CAM only shows correlation, never causation."
    )

    add_h3("What We Implemented: The \"What-If\" Digital Resection Test")
    p = doc.add_paragraph()
    p.add_run("To prove causality, we built a Counterfactual Causal Inpainting Engine (backend/services/causal_inpainter.py).")

    add_code_block(
        "  [ Original Scan (Tumor Present) ]                 [ Counterfactual Scan (Digital Resection) ]\n"
        "                 │                                                       │\n"
        "                 ▼                                                       ▼\n"
        "      Model Evaluates Scan                                    Model Re-Evaluates Scan\n"
        "   P(Tumor | Real) = 86.4%                                 P(Tumor | Inpainted) = 8.2%\n"
        "                 │                                                       │\n"
        "                 └──────────────────────────┬────────────────────────────┘\n"
        "                                            ▼\n"
        "                        Causal Attribution Factor (Delta-P):\n"
        "                           ΔP = 86.4% - 8.2% = +78.2% Drop\n"
        "                                            │\n"
        "                                            ▼\n"
        "                         [ \"Strong Causal Grounding Verified\" ]"
    )

    add_h3("How It Works Step-by-Step:")
    steps_p2 = [
        ("1. Lesion Mask Dilation: ", "The system extracts the active tumor boundary mask from the saliency map and dilates it by 7 pixels to encapsulate the peritumoral edema transition zone."),
        ("2. Symmetry-Guided Contralateral Inpainting: ", "Human neuroanatomy possesses bilateral hemispheric symmetry. If the tumor is on the right side of the brain, the left hemisphere at coordinate (W - x, y) contains healthy, patient-matched brain parenchyma. The engine horizontally mirrors the contralateral healthy tissue and blends it into the defect using soft Gaussian alpha masks."),
        ("3. Navier-Stokes Diffusion & Bilateral Smoothing: ", "The boundary seams are filled using Navier-Stokes partial differential equations (cv2.INPAINT_NS), which propagate surrounding parenchymal intensity gradients along the lines of equal brightness (isophotes). A bilateral filter smooths tissue texture while preserving anatomical white/gray matter edges."),
        ("4. Re-Inference on Counterfactual Healthy Brain (X_cf): ", "The synthesized 'tumor-free' scan is fed back into EfficientNet-B0."),
        ("5. Causal Attribution Factor (ΔP_tumor): ", "\nΔP_tumor = P(Tumor | X) - P(Tumor | X_cf)\n• ΔP ≥ 50%: Strong Causal Grounding (High Attribution Fidelity) — Mathematical proof that the model's call was caused strictly by the lesion tissue.\n• ΔP < 25%: Shortcut Learning Alert — Flags that erasing the lesion did not meaningfully drop confidence, warning clinicians of background bias."),
        ("6. Interactive UI Before/After Slider: ", "Reviewers can drag an interactive handle (⇄) across the scan to digitally erase the tumor and watch the probability chart collapse in real time.")
    ]
    for stitle, sdesc in steps_p2:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        r_t = p.add_run(stitle)
        r_t.bold = True
        r_t.font.color.rgb = DARK_BLUE
        p.add_run(sdesc)

    # Pillar 3
    add_h2("Pillar 3: Quantitative Radiomics & Morphometry Engine")
    add_h3("The Clinical Problem")
    p = doc.add_paragraph()
    p.add_run(
        "A thermal heatmap is essentially a \"blurry artistic blob\". Neuroradiologists cannot measure surgical margins or classify WHO CNS tumor types from a heatmap alone.\n"
        "Clinical staging depends on:\n"
        "• How large is the mass in square millimeters?\n"
        "• Are the borders circumscribed and smooth (typical of benign/encapsulated Meningiomas) or infiltrative and jagged (typical of invasive malignant Gliomas)?\n"
        "• In which anatomical compartment does the mass reside?"
    )

    add_h3("What We Implemented")
    p = doc.add_paragraph()
    p.add_run(
        "We developed a Morphometric Radiomics Engine (backend/services/radiomics_engine.py) that translates raw gradient activations into clinical biomarkers."
    )

    add_h3("The 5 Extracted Biomarkers:")
    bio_list = [
        ("1. Cross-Sectional Surface Area (mm² & pixel count): ", "Based on standard adult cranial MRI FOV (220 mm × 220 mm) mapped to 224 × 224 pixels: 1 pixel ≈ 0.982 mm ⟹ 1 px² ≈ 0.965 mm². Calculates exact pixel area A_px and metric area A_mm2 = A_px × 0.965, along with percentage slice occupancy."),
        ("2. Sphericity & Compactness Index (Ψ ∈ (0, 1]): ", "Ψ = (4π * Area) / (Perimeter²). Ψ ≥ 0.65: Circumscribed / Encapsulated (smooth border, typical of Meningioma or Pituitary Adenoma). Ψ < 0.60: Infiltrative / Lobulated (diffuse margins, typical of Glioma)."),
        ("3. Margin Irregularity Score: ", "Irregularity = 1.0 - Solidity = 1.0 - (Contour Area / Convex Hull Area). Measures how deeply the tumor margin invades neighboring brain tissue."),
        ("4. Aspect Ratio: ", "Calculated by fitting a minimum-area rotated bounding ellipse to determine tumor elongation (Major Axis / Minor Axis)."),
        ("5. Neuroanatomical Compartment Mapping: ", "Using normalized centroid coordinates (cx, cy) and distance from the cranial vault:\n• Sellar / Pituitary Fossa: Centered in the central skull base (cy ∈ [0.50, 0.78], cx ∈ [0.40, 0.60]).\n• Extra-Axial Convexity / Dural Border: Lesion abuts the outer skull perimeter (d_center > 0.28).\n• Intra-Axial Deep White Matter: Embedded within the cerebral hemispheres.")
    ]
    for btitle, bdesc in bio_list:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2)
        r_t = p.add_run(btitle)
        r_t.bold = True
        r_t.font.color.rgb = DARK_BLUE
        p.add_run(bdesc)

    # -----------------------------------------------------------------
    # SECTION 4
    # -----------------------------------------------------------------
    add_h1("4. End-to-End Pipeline: What Happens When You Upload a Scan")
    p = doc.add_paragraph()
    p.add_run("Here is the exact technical execution flow from the moment a file is uploaded to the live UI display:")

    add_code_block(
        "[ Uploaded MRI Scan ]\n"
        "         │\n"
        "         ▼\n"
        "[ Step 1: Input Validation & Image Quality Gate ]\n"
        "  ├── File Header & Channel Integrity (RGB 224x224 standardization)\n"
        "  ├── Image Quality: SNR, Contrast Ratio, Laplacian Blur Variance\n"
        "  └── OOD Detection: Monochromatic consistency, border air-to-skull ratio\n"
        "         │ (If Passed)\n"
        "         ▼\n"
        "[ Step 2: Unified Inference & Grad-CAM Extraction ]\n"
        "  ├── EfficientNet-B0 forward pass: Generates calibrated class probability vector\n"
        "  └── Native GradientTape: Backpropagates top predicted class to 'top_conv' layer -> Heatmap\n"
        "         │\n"
        "         ├───► [ Step 3: Conformal Uncertainty Engine ]\n"
        "         │       ├── Computes non-conformity against calibration threshold\n"
        "         │       ├── Returns 95% Confidence Prediction Set e.g. {\"Glioma\", \"Meningioma\"}\n"
        "         │       └── Calculates Shannon Entropy & Epistemic Uncertainty Gauge\n"
        "         │\n"
        "         ├───► [ Step 4: Quantitative Radiomics Profiler ]\n"
        "         │       ├── Adaptive Otsu thresholding on smoothed saliency map\n"
        "         │       ├── Primary lesion contour & bounding box extraction\n"
        "         │       ├── Calculates Area (mm²), Sphericity Index (Ψ), Margin Irregularity\n"
        "         │       ├── Classifies Neuroanatomical Compartment (Sellar / Intra-axial / Extra-axial)\n"
        "         │       └── Generates Cyan Precision Margin Contour Overlay\n"
        "         │\n"
        "         └───► [ Step 5: Counterfactual Digital Lesion Resection ]\n"
        "                 ├── Dilation of lesion mask + Contralateral symmetry blending\n"
        "                 ├── Navier-Stokes inpainting fills defect with healthy brain parenchyma\n"
        "                 ├── Re-inference on synthesized \"tumor-removed\" scan (X_cf)\n"
        "                 ├── Computes Causal Attribution Factor: ΔP = P(Tumor|Real) - P(Tumor|Ablated)\n"
        "                 └── Confirms \"Strong Causal Grounding\" (ΔP >= 50%)\n"
        "                         │\n"
        "                         ▼\n"
        "       [ Step 6: Interactive Next.js Clinical Decision Cockpit ]\n"
        "         ├── Prediction Card & Probability Breakdown\n"
        "         ├── 95% Conformal Prediction Set & Uncertainty Meter\n"
        "         ├── Quantitative Radiomics HUD with Contour Toggle\n"
        "         └── Interactive Before/After Resection Slider (⇄)"
    )

    # -----------------------------------------------------------------
    # SECTION 5
    # -----------------------------------------------------------------
    add_h1("5. Summary Cheat Sheet for Professors & Reviewers")
    p = doc.add_paragraph()
    p.add_run("If a professor or evaluator asks about your project's novelty during a review, here are the key questions and how to answer them:")

    qa_cheatsheet = [
        (
            "Q1: \"Why did you implement this instead of just stopping at Grad-CAM?\"",
            "\"Grad-CAM only shows where gradients were high—it demonstrates correlation, not causality. Deep networks frequently suffer from shortcut learning, where they focus on skull bone, contrast variations, or scanner artifacts. To solve this, we created NeuroCausal-X: a counterfactual inpainting engine that digitally resects the tumor using healthy contralateral tissue and re-tests the model. Measuring the resulting confidence drop (ΔP) mathematically proves whether the model's prediction was caused by the tumor itself.\""
        ),
        (
            "Q2: \"Why can we trust your confidence percentages? Isn't softmax uncalibrated?\"",
            "\"Yes, standard softmax probabilities are notoriously overconfident and cannot be treated as clinical risk probabilities. Rather than using ad-hoc heuristics, we implemented Split Conformal Prediction, which provides a distribution-free 95% statistical coverage guarantee (P(Y ∈ Ĉ) ≥ 95%). If a scan is ambiguous between Glioma and Meningioma, the model outputs a differential prediction set with an epistemic ambiguity flag, alerting the clinician to order secondary reviews rather than taking a silent 50/50 gamble.\""
        ),
        (
            "Q3: \"What makes your explainability clinically useful to a real neuroradiologist?\"",
            "\"Radiologists cannot measure surgical resection margins from a thermal heatmap. Our radiomics engine extracts quantified physical biomarkers directly from the segmented lesion contour: surface area in mm², border sphericity index (Ψ), margin irregularity, and anatomical compartment localization (e.g. Sellar region vs. Extra-axial dural attachment vs. Deep white matter). This bridges the gap between deep learning features and standard WHO CNS diagnostic criteria.\""
        )
    ]

    for q_text, a_text in qa_cheatsheet:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q_text)
        r_q.bold = True
        r_q.font.color.rgb = DARK_BLUE

        add_callout(a_text, speaker="Your Exact Answer:")

    # Save to both target locations
    path1 = os.path.abspath("NeuroCausal_X_Architectural_Guide.docx")
    path2 = os.path.abspath("NeuroCausal_X_Feature_Documentation.docx")
    doc.save(path1)
    doc.save(path2)
    print(f"[OK] Generated {path1} and updated {path2}")

if __name__ == "__main__":
    create_guide_doc()
