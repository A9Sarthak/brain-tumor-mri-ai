'use client';

import React from 'react';
import { FileText, CheckCircle2, AlertTriangle, HelpCircle, Activity, ShieldCheck, Check } from 'lucide-react';
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
  
  const isNoTumor = prediction?.prediction.toLowerCase().includes('no tumor');

  const getConditionStyle = () => {
    if (!prediction) return '';
    if (isNoTumor) {
      return 'border-emerald-200 dark:border-emerald-850 bg-emerald-50/70 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-200';
    }
    return 'border-sky-200 dark:border-sky-850 bg-sky-50/60 dark:bg-sky-950/30 text-sky-950 dark:text-sky-100';
  };

  const getDotColor = (className: string) => {
    switch (className) {
      case 'No Tumor':
        return 'bg-emerald-500';
      case 'Glioma Tumor':
        return 'bg-amber-500';
      case 'Meningioma Tumor':
        return 'bg-indigo-500';
      case 'Pituitary Tumor':
        return 'bg-sky-500';
      default:
        return 'bg-slate-400';
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden flex flex-col h-full transition-all">
      
      {/* Step Header */}
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-sky-600 text-white font-bold text-xs flex items-center justify-center shadow-2xs">
            2
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base leading-tight">
              AI Analysis Result
            </h2>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Deep CNN classification output
            </p>
          </div>
        </div>

        {prediction ? (
          <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 border border-emerald-200 dark:border-emerald-900/60 px-2 py-0.5 rounded-full">
            <Check className="w-3 h-3 text-emerald-600" />
            <span>Analysis completed</span>
          </span>
        ) : (
          <span className="text-[10px] font-semibold text-slate-400 dark:text-slate-500">
            Awaiting input
          </span>
        )}
      </div>

      {/* Card Content */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        {!prediction ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 min-h-[260px] border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/40 dark:bg-slate-850/20">
            <div className="w-12 h-12 rounded-full bg-white dark:bg-slate-800 text-slate-400 dark:text-slate-500 flex items-center justify-center mb-3 shadow-2xs border border-slate-200 dark:border-slate-700">
              <HelpCircle className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Awaiting MRI Scan
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs leading-relaxed">
              Upload an MRI scan in Step 1 or select a representative example scan below to run AI inference.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-4">
            
            {/* Predicted Condition Highlight Box */}
            <div className={`p-4 rounded-xl border flex flex-col gap-2 ${getConditionStyle()}`}>
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 dark:text-slate-400">
                  PREDICTED CONDITION
                </span>
                <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-white/90 dark:bg-slate-900/80 border border-current shadow-2xs">
                  {(prediction.confidence * 100).toFixed(1)}% Confidence
                </span>
              </div>
              <div className="flex items-center gap-2.5">
                {isNoTumor ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-600 dark:text-emerald-400 shrink-0" />
                ) : (
                  <AlertTriangle className="w-6 h-6 text-sky-600 dark:text-sky-400 shrink-0" />
                )}
                <span className="text-xl sm:text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                  {prediction.prediction}
                </span>
              </div>
            </div>

            {/* Class Probabilities Distribution */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Class Probabilities
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  Latency: {prediction.processing_time_ms}ms
                </span>
              </div>

              <div className="space-y-2">
                {CLASS_ORDER.map((className) => {
                  const prob = prediction.probabilities[className] ?? 0;
                  const percent = (prob * 100).toFixed(1);
                  const isTop = prediction.prediction === className;

                  return (
                    <div 
                      key={className} 
                      className={`p-2 rounded-lg border transition-all ${
                        isTop 
                          ? 'border-sky-300 dark:border-sky-800 bg-sky-50/50 dark:bg-sky-950/40 shadow-2xs font-semibold' 
                          : 'border-transparent hover:bg-slate-50 dark:hover:bg-slate-800/40'
                      }`}
                    >
                      <div className="flex justify-between items-center text-xs mb-1">
                        <div className="flex items-center gap-1.5 truncate">
                          <span className={`w-2 h-2 rounded-full shrink-0 ${getDotColor(className)}`} />
                          <span className={`truncate ${isTop ? 'text-slate-900 dark:text-white font-bold' : 'text-slate-600 dark:text-slate-400'}`}>
                            {className}
                          </span>
                        </div>
                        <span className={`font-mono text-xs ${isTop ? 'text-sky-700 dark:text-sky-300 font-bold' : 'text-slate-600 dark:text-slate-400'}`}>
                          {percent}%
                        </span>
                      </div>

                      <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${
                            isTop
                              ? isNoTumor ? 'bg-emerald-500' : 'bg-sky-600 dark:bg-sky-400'
                              : 'bg-slate-300 dark:bg-slate-700'
                          }`}
                          style={{ width: `${Math.max(Number(percent), 1)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Key Image Insights Box */}
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-800 space-y-1.5 text-xs">
              <div className="flex items-center justify-between pb-1 border-b border-slate-200/60 dark:border-slate-700/60">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Key Image Insights
                </span>
                <span className="text-[10px] text-slate-400 font-mono">Factual Technical Summary</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] pt-0.5">
                <div>
                  <span className="text-slate-400 dark:text-slate-500 block">Classified Type</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200 truncate block">
                    {prediction.prediction}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 dark:text-slate-500 block">Model Confidence</span>
                  <span className="font-semibold text-slate-800 dark:text-slate-200 block">
                    {(prediction.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 dark:text-slate-500 block">Input Resolution</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200 block">224 × 224 × 3</span>
                </div>
                <div>
                  <span className="text-slate-400 dark:text-slate-500 block">Backbone Model</span>
                  <span className="font-mono text-slate-800 dark:text-slate-200 block">EfficientNet-B0</span>
                </div>
              </div>
            </div>

          </div>
        )}

        {/* Report Button */}
        {prediction && (
          <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button
              onClick={onOpenReport}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold bg-sky-50 hover:bg-sky-100 dark:bg-slate-800 dark:hover:bg-slate-750 text-sky-800 dark:text-sky-300 border border-sky-200/80 dark:border-slate-700 transition-colors cursor-pointer"
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
