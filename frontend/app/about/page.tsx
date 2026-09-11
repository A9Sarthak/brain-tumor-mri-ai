import React from 'react';
import { 
  Info, 
  Cpu, 
  Eye, 
  ShieldCheck, 
  Layers, 
  CheckCircle2,
  Lock,
  GitBranch
} from 'lucide-react';
export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">


      {/* Page Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <Info className="w-3.5 h-3.5" />
          <span>PROJECT ARCHITECTURE &amp; METHODOLOGY</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
          About NeuroScan AI
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Next-generation clinical decision-support framework for brain MRI classification and visual interpretability.
        </p>
      </div>

      {/* Overview Section */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-sky-600 dark:text-sky-400" />
          System Overview &amp; Purpose
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          NeuroScan AI is an automated neuroimaging analysis system developed to assist clinical researchers and healthcare professionals in screening Magnetic Resonance Imaging (MRI) scans of the brain. The platform ingests standard axial T1/T2-weighted MRI scans and classifies them across four primary diagnostic categories:
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
            <h4 className="font-semibold text-xs uppercase tracking-wider text-slate-900 dark:text-white mb-1">
              0. No Tumor (Healthy Control)
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Absence of abnormal intracranial mass effect, mass lesions, or hyperintense neoplastic tissue.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
            <h4 className="font-semibold text-xs uppercase tracking-wider text-slate-900 dark:text-white mb-1">
              1. Glioma Tumor
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Primary brain tumor originating from glial cells (astrocytomas, oligodendrogliomas, glioblastomas) showing infiltrative boundaries.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
            <h4 className="font-semibold text-xs uppercase tracking-wider text-slate-900 dark:text-white mb-1">
              2. Meningioma Tumor
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Typically benign, extra-axial tumors originating from the arachnoid layer of the meninges, often presenting dural tail signs.
            </p>
          </div>

          <div className="p-3.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800">
            <h4 className="font-semibold text-xs uppercase tracking-wider text-slate-900 dark:text-white mb-1">
              3. Pituitary Tumor
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Adenomas occurring within the sella turcica, potentially expanding into the suprasellar cistern and compressing the optic chiasm.
            </p>
          </div>
        </div>
      </section>

      {/* Model Architecture & Transfer Learning */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Layers className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          EfficientNet-B0 Backbone &amp; Two-Stage Transfer Learning
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          The core classification engine utilizes <strong className="text-slate-800 dark:text-slate-100 font-semibold">EfficientNet-B0</strong>, an architecture designed via compound coefficient scaling that uniformly balances network depth, width, and image resolution.
        </p>
        <div className="space-y-3 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <strong>Stage 1 (Feature Extractor Warm-up): </strong>
              The pre-trained ImageNet convolutional backbone is initially frozen while newly initialized classification projection heads (Dense 256, Dropout 0.3, Softmax 4) are optimized using Adam with a learning rate of 1e-3.
            </div>
          </div>
          <div className="flex items-start gap-2.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div>
              <strong>Stage 2 (Targeted Fine-Tuning): </strong>
              The top 20 convolutional layers (including the critical <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono">top_conv</code> layer) are unfrozen and trained end-to-end with an attenuated learning rate of 1e-4, mitigating representation collapse and achieving 80.00% accuracy on held-out test data.
            </div>
          </div>
        </div>
      </section>

      {/* Grad-CAM Interpretability */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Eye className="w-5 h-5 text-teal-600 dark:text-teal-400" />
          Explainable AI with Grad-CAM
        </h2>
        <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          In clinical medicine, black-box predictions are inadequate. NeuroScan AI integrates <strong className="text-slate-800 dark:text-slate-100 font-semibold">Gradient-weighted Class Activation Mapping (Grad-CAM)</strong> to compute the gradients of the predicted class score with respect to the feature activation maps of layer <code className="px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800 font-mono">top_conv</code>.
        </p>
        <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
          By spatially pooling these gradients and applying a ReLU activation function, the system renders a high-resolution heatmap highlighting the precise anatomical regions that motivated the model&apos;s decision, enabling clinicians to visually audit whether the network attended to actual lesion pathology rather than scan artifacts.
        </p>
      </section>

      {/* Data Privacy & Security */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs space-y-3">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Lock className="w-5 h-5 text-sky-600 dark:text-sky-400" />
          Privacy &amp; Data Governance
        </h2>
        <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
          All inference occurs transiently in-memory. Uploaded MRI scans are never persisted to disk or external databases by default. The session history is maintained strictly on the user&apos;s local browser workstation, ensuring patient privacy and compliance with research data handling guidelines.
        </p>
      </section>

      {/* Model Protection Lock */}
      <section className="bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 rounded-xl p-5 text-xs text-slate-500 dark:text-slate-400 flex items-start gap-3">
        <GitBranch className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-slate-700 dark:text-slate-300">Model Lineage &amp; Integrity: </strong>
          The underlying model weights (<code className="font-mono">best_efficientnet_model.keras</code>) and 4-class taxonomy are authoritative and strictly locked. The modern web stack migration maintains exact input preprocessing (224x224x3, RGB, standard scale) and numerical equivalence with validated benchmark evaluation scripts.
        </div>
      </section>

    </div>
  );
}
