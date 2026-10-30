import React, { useState } from 'react';
import { Scissors, Sparkles, CheckCircle2, AlertCircle, ArrowRight, Eye, SplitSquareVertical } from 'lucide-react';
import { CounterfactualResult } from '@/lib/types';
import { toDataUrl } from '@/lib/api';

interface CounterfactualSliderProps {
  originalImageBase64: string;
  counterfactual: CounterfactualResult;
  originalPrediction: string;
  originalConfidence: number;
}

export default function CounterfactualSlider({
  originalImageBase64,
  counterfactual,
  originalPrediction,
  originalConfidence,
}: CounterfactualSliderProps) {
  const [sliderPos, setSliderPos] = useState<number>(50);
  const [viewMode, setViewMode] = useState<'slider' | 'side-by-side'>('slider');

  const origUrl = toDataUrl(originalImageBase64);
  const cfUrl = toDataUrl(counterfactual.counterfactual_image_base64);
  const deltaPct = Math.round(counterfactual.causal_attribution_delta * 100);

  const isStrong = counterfactual.causal_attribution_delta >= 0.40;

  return (
    <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-5 shadow-lg backdrop-blur">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Scissors className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Counterfactual Digital Lesion Resection
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-teal-500/20 text-teal-300 font-mono">
                Causal Ablation
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Symmetry-guided inpainting to test causal sensitivity (ΔP Attribution)
            </p>
          </div>
        </div>

        {/* View Switcher */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 self-start sm:self-auto">
          <button
            onClick={() => setViewMode('slider')}
            className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors flex items-center gap-1.5 ${
              viewMode === 'slider'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <SplitSquareVertical className="w-3.5 h-3.5" />
            Slider
          </button>
          <button
            onClick={() => setViewMode('side-by-side')}
            className={`px-2.5 py-1 text-xs font-medium rounded-md transition-colors flex items-center gap-1.5 ${
              viewMode === 'side-by-side'
                ? 'bg-teal-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            Side-by-Side
          </button>
        </div>
      </div>

      {/* Causal Verification KPI Bar */}
      <div className="mb-4 bg-slate-950/70 rounded-xl p-3 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="text-xs text-slate-400">
            <span>Original Prediction: </span>
            <span className="font-semibold text-slate-200">{originalPrediction}</span>
            <span className="text-slate-400 font-mono ml-1">({Math.round(originalConfidence * 100)}%)</span>
          </div>
          <ArrowRight className="w-3.5 h-3.5 text-teal-400" />
          <div className="text-xs text-slate-400">
            <span>Ablated Counterfactual: </span>
            <span className="font-semibold text-teal-300">{counterfactual.counterfactual_prediction}</span>
            <span className="text-slate-400 font-mono ml-1">({Math.round(counterfactual.counterfactual_confidence * 100)}%)</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="px-2.5 py-1 rounded-md bg-teal-950/60 border border-teal-800/80 text-teal-300 text-xs font-mono font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-teal-400" />
            ΔP Drop: -{deltaPct}%
          </div>
          <div
            className={`px-2.5 py-1 rounded-md text-xs font-medium border flex items-center gap-1 ${
              isStrong
                ? 'bg-emerald-950/50 text-emerald-300 border-emerald-800'
                : 'bg-amber-950/50 text-amber-300 border-amber-800'
            }`}
          >
            {isStrong ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
            {counterfactual.causal_verification_status.split('(')[0].trim()}
          </div>
        </div>
      </div>

      {/* Interactive Visual Display */}
      {viewMode === 'slider' ? (
        <div className="relative w-full max-w-lg mx-auto aspect-square rounded-xl overflow-hidden border border-slate-700 shadow-2xl select-none group">
          {/* Base Image: Counterfactual Inpainted Scan */}
          <img
            src={cfUrl}
            alt="Counterfactual Inpainted Scan"
            className="absolute inset-0 w-full h-full object-cover"
          />

          {/* Overlaid Image: Original Scan clipped by slider position */}
          <div
            className="absolute inset-0 overflow-hidden"
            style={{ width: `${sliderPos}%` }}
          >
            <img
              src={origUrl}
              alt="Original MRI Scan"
              className="absolute inset-0 w-full h-full object-cover max-w-none"
              style={{ width: '100%', height: '100%' }}
            />
            {/* Left Label */}
            <span className="absolute top-3 left-3 bg-slate-900/85 text-slate-200 text-[11px] px-2 py-1 rounded-md font-medium border border-slate-700 shadow">
              Original MRI
            </span>
          </div>

          {/* Right Label */}
          <span className="absolute top-3 right-3 bg-teal-950/90 text-teal-200 text-[11px] px-2 py-1 rounded-md font-medium border border-teal-800 shadow">
            Resected (Tumor Removed)
          </span>

          {/* Divider Line */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-teal-400 shadow-[0_0_10px_rgba(45,212,191,0.8)] pointer-events-none"
            style={{ left: `${sliderPos}%` }}
          >
            <div className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-7 h-7 rounded-full bg-slate-900 border-2 border-teal-400 text-teal-300 flex items-center justify-center text-[10px] font-bold shadow-lg">
              ⇄
            </div>
          </div>

          {/* Invisible interactive range input covering the frame */}
          <input
            type="range"
            min="0"
            max="100"
            value={sliderPos}
            onChange={(e) => setSliderPos(Number(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize z-20"
            aria-label="Drag to compare original and counterfactual tumor-resected scan"
          />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
          <div className="space-y-1.5">
            <span className="text-xs font-medium text-slate-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-indigo-400" />
              Original Scan (Pathology Present)
            </span>
            <div className="rounded-xl overflow-hidden border border-slate-700 aspect-square">
              <img src={origUrl} alt="Original Scan" className="w-full h-full object-cover" />
            </div>
          </div>

          <div className="space-y-1.5">
            <span className="text-xs font-medium text-teal-300 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-teal-400" />
              Digital Resection (Parenchymal Inpainted)
            </span>
            <div className="rounded-xl overflow-hidden border border-teal-700/60 aspect-square">
              <img src={cfUrl} alt="Counterfactual Resected Scan" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      )}

      {/* Explanation Footer */}
      <p className="mt-3 text-xs text-slate-400 leading-relaxed text-center sm:text-left">
        <span className="text-slate-300 font-medium">Causal Verification Note: </span>
        {counterfactual.explanation}
      </p>
    </div>
  );
}

