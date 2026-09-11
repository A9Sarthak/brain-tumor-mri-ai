'use client';

import React from 'react';
import { FileText, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';
import { PredictionResponse } from '../lib/types';

interface ResultCardProps {
  prediction: PredictionResponse | null;
  isLoading: boolean;
  onOpenReport: () => void;
}

const CLASS_ORDER = [
  'No Tumor',
  'Glioma Tumor',
  'Meningioma Tumor',
  'Pituitary Tumor'
];

export default function ResultCard({
  prediction,
  isLoading,
  onOpenReport,
}: ResultCardProps) {
  const getBadgeStyle = (label: string) => {
    if (label.toLowerCase().includes('no tumor')) {
      return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
    }
    return 'bg-sky-50 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300 border-sky-200 dark:border-sky-800';
  };

  const getBarColor = (label: string, isHighest: boolean) => {
    if (isHighest) {
      return label.toLowerCase().includes('no tumor')
        ? 'bg-emerald-500 dark:bg-emerald-400'
        : 'bg-sky-600 dark:bg-sky-400';
    }
    return 'bg-slate-300 dark:bg-slate-700';
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xs overflow-hidden flex flex-col h-full transition-colors">
      {/* Step Header */}
      <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-400 font-bold text-xs flex items-center justify-center border border-sky-200 dark:border-sky-800">
            2
          </div>
          <h2 className="font-semibold text-slate-900 dark:text-white text-base">
            AI Analysis Result
          </h2>
        </div>
        {prediction && (
          <span className="text-[11px] font-mono text-slate-400 dark:text-slate-500">
            ID: {prediction.analysis_id.slice(0, 8)}
          </span>
        )}
      </div>

      {/* Card Content */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        {!prediction ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 min-h-[260px] border border-dashed border-slate-200 dark:border-slate-800 rounded-xl">
            <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 flex items-center justify-center mb-3">
              <HelpCircle className="w-6 h-6" />
            </div>
            <p className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
              Awaiting MRI Submission
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs">
              Upload a scan in Step 1 or select a sample scan below to generate AI classification.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-5">
            {/* Prediction Highlight Banner */}
            <div className={`p-4 rounded-xl border flex flex-col gap-1.5 ${getBadgeStyle(prediction.prediction)}`}>
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase font-semibold tracking-wider text-slate-500 dark:text-slate-400">
                  Predicted Condition
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-white/80 dark:bg-black/40 border border-current">
                  {(prediction.confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
              <div className="flex items-center gap-2">
                {prediction.prediction.toLowerCase().includes('no tumor') ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-sky-600 dark:text-sky-400 shrink-0" />
                )}
                <span className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
                  {prediction.prediction}
                </span>
              </div>
            </div>

            {/* Class Probabilities Distribution */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Class Probabilities
                </span>
                <span className="text-[11px] text-slate-400 font-mono">
                  {prediction.processing_time_ms}ms
                </span>
              </div>

              <div className="space-y-2.5">
                {CLASS_ORDER.map((className) => {
                  const prob = prediction.probabilities[className] ?? 0;
                  const percent = (prob * 100).toFixed(1);
                  const isTop = prediction.prediction === className;

                  return (
                    <div key={className} className="space-y-1">
                      <div className="flex justify-between items-center text-xs">
                        <span className={`font-medium ${isTop ? 'text-slate-900 dark:text-white font-semibold' : 'text-slate-600 dark:text-slate-400'}`}>
                          {className}
                        </span>
                        <span className="font-mono text-slate-700 dark:text-slate-300 text-xs">
                          {percent}%
                        </span>
                      </div>
                      <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getBarColor(className, isTop)}`}
                          style={{ width: `${Math.max(Number(percent), 1)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Result Clinical Informational Note */}
            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-[12px] text-slate-600 dark:text-slate-300 leading-relaxed">
              This AI-assisted result represents the model&apos;s prediction for the uploaded image. Please refer to the explanation section and consult a qualified healthcare professional for clinical interpretation.
            </div>
          </div>
        )}

        {/* Report Button */}
        {prediction && (
          <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              onClick={onOpenReport}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 transition-colors cursor-pointer"
            >
              <FileText className="w-4 h-4 text-sky-600 dark:text-sky-400" />
              <span>Generate Analysis Report</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
