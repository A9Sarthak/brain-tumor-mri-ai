'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { BookOpen, ArrowRight } from 'lucide-react';

type TumorTab = 'pituitary' | 'glioma' | 'meningioma' | 'notumor';

interface TumorInfo {
  title: string;
  category: string;
  description: string;
  characteristics: string[];
  mriFindings: string;
}

const TUMOR_DATA: Record<TumorTab, TumorInfo> = {
  pituitary: {
    title: 'Pituitary Tumor',
    category: 'Sellar / Endocrine Neoplasm',
    description:
      'Pituitary adenomas originate in the pituitary gland at the base of the skull (sella turcica). While predominantly benign and slow-growing, expanding adenomas may compress adjacent cranial structures including the optic chiasm.',
    characteristics: [
      'Originates in anterior lobe (adenohypophysis)',
      'Classified as microadenoma (<10mm) or macroadenoma (≥10mm)',
      'May alter endocrine hormone secretion profiles',
    ],
    mriFindings:
      'T1-weighted contrast-enhanced scans typically demonstrate sellar floor remodeling, asymmetric gland enlargement, or suprasellar extension toward the optic apparatus.',
  },
  glioma: {
    title: 'Glioma Tumor',
    category: 'Intra-Axial Glial Neoplasm',
    description:
      'Gliomas are primary brain tumors that arise from glial progenitor cells, including astrocytomas, oligodendrogliomas, and glioblastomas. They exhibit variable degrees of invasiveness and infiltrative tissue borders.',
    characteristics: [
      'Arise from supporting glial tissue (astrocytes, oligodendrocytes)',
      'Spectrum ranges from low-grade (Grade I/II) to high-grade glioblastoma (Grade IV)',
      'Infiltrates surrounding cerebral parenchyma',
    ],
    mriFindings:
      'T2/FLAIR sequences frequently show significant hyperintensity and perifocal vasogenic edema, with variable heterogeneous ring or nodular gadolinium enhancement.',
  },
  meningioma: {
    title: 'Meningioma Tumor',
    category: 'Extra-Axial Dural Neoplasm',
    description:
      'Meningiomas originate from arachnoid cap cells of the meninges—the protective membranes enveloping the brain and spinal cord. They are usually well-circumscribed, slow-growing, and predominantly benign (WHO Grade I).',
    characteristics: [
      'Arise outside the brain parenchyma (extra-axial)',
      'Most common primary non-malignant brain tumor in adults',
      'Typically benign and surgically accessible',
    ],
    mriFindings:
      'Classic imaging hallmarks include sharp dural attachment with a characteristic "dural tail" sign and intense, uniform enhancement following gadolinium administration.',
  },
  notumor: {
    title: 'No Tumor (Normal Scan)',
    category: 'Healthy Neuroimaging Control',
    description:
      'Healthy brain MRI scans demonstrate structural symmetry, preserved gray-white matter junction differentiation, normal ventricular caliber, and absence of mass effect, midline shift, or pathologic focal signal alterations.',
    characteristics: [
      'Bilateral anatomical hemisphere symmetry',
      'Normal cerebrospinal fluid (CSF) flow spaces',
      'Absence of abnormal intracranial lesions or enhancement',
    ],
    mriFindings:
      'Uniform baseline signal intensity across T1 and T2 sequences without evidence of intracranial mass lesion, abnormal focal edema, or neoplastic enhancement.',
  },
};

export default function BrainTumorInfo() {
  const [activeTab, setActiveTab] = useState<TumorTab>('pituitary');
  const current = TUMOR_DATA[activeTab];

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-6 sm:p-7 shadow-xs transition-colors">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-5 pb-4 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <BookOpen className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
              Brain Tumor Information
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Educational neuroimaging reference for the four evaluated clinical categories.
          </p>
        </div>

        <Link
          href="/about"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-sky-600 dark:text-sky-400 hover:text-sky-700 dark:hover:text-sky-300 transition-colors"
        >
          <span>Learn More About Architecture</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {/* Category Tabs */}
      <div className="flex flex-wrap items-center gap-2 mb-6">
        {(Object.keys(TUMOR_DATA) as TumorTab[]).map((key) => {
          const item = TUMOR_DATA[key];
          const isActive = activeTab === key;
          return (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-sky-600 text-white shadow-2xs'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-750'
              }`}
            >
              {item.title}
            </button>
          );
        })}
      </div>

      {/* Tab Content Panel */}
      <div className="space-y-4">
        <div>
          <span className="text-[10px] font-mono uppercase font-bold tracking-wider text-sky-600 dark:text-sky-400">
            {current.category}
          </span>
          <h4 className="text-lg font-bold text-slate-900 dark:text-white mt-0.5">
            {current.title}
          </h4>
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed mt-2">
            {current.description}
          </p>
        </div>

        <div className="space-y-1.5 pt-1">
          <span className="text-xs font-bold text-slate-900 dark:text-white block">
            Pathological Key Points:
          </span>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-600 dark:text-slate-300 pt-1">
            {current.characteristics.map((c, i) => (
              <li key={i} className="flex items-start gap-2 p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200/60 dark:border-slate-800">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-500 shrink-0 mt-1.5" />
                <span>{c}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

    </section>
  );
}
