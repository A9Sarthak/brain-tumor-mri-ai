'use client';

import React from 'react';
import { FileText, CheckCircle2, ArrowRight } from 'lucide-react';

interface ReportCardProps {
  onGenerateReport: () => void;
  hasAnalysis: boolean;
}

export default function ReportCard({ onGenerateReport, hasAnalysis }: ReportCardProps) {
  const items = [
    'Uploaded MRI Scan preview',
    'AI classification output',
    '4-Class probability distribution',
    'Grad-CAM attention visualization',
    'Model & architecture parameters',
    'Cryptographic analysis timestamp',
    'Responsible AI research disclaimer',
  ];

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-6 sm:p-7 shadow-xs flex flex-col justify-between transition-colors">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/70 text-sky-600 dark:text-sky-400">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
            Generate Analysis Report
          </h3>
        </div>

        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4 leading-relaxed">
          Export a comprehensive clinical analysis document for multidisciplinary research review.
        </p>

        <div className="space-y-2 mb-6">
          {items.map((item) => (
            <div key={item} className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-300">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={onGenerateReport}
        disabled={!hasAnalysis}
        className={`w-full flex items-center justify-center gap-2 px-5 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer shadow-xs ${
          !hasAnalysis
            ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 border border-slate-200 dark:border-slate-700 cursor-not-allowed'
            : 'bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white shadow-sky-600/20'
        }`}
      >
        <span>Generate Report</span>
        <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );
}
