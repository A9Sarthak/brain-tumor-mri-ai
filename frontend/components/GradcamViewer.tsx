'use client';

import React, { useState } from 'react';
import { Eye, Info, Layers, Loader2 } from 'lucide-react';
import { GradcamResponse } from '../lib/types';
import { toDataUrl } from '../lib/api';

interface GradcamViewerProps {
  gradcam: GradcamResponse | null;
  isLoading: boolean;
}

type TabType = 'overlay' | 'attention' | 'original';

export default function GradcamViewer({ gradcam, isLoading }: GradcamViewerProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overlay');
  const [showExplanation, setShowExplanation] = useState(false);

  const getImageSrc = () => {
    if (!gradcam) return null;
    switch (activeTab) {
      case 'original':
        return toDataUrl(gradcam.original_image_base64);
      case 'attention':
        return toDataUrl(gradcam.attention_heatmap_base64);
      case 'overlay':
      default:
        return toDataUrl(gradcam.overlay_image_base64);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden flex flex-col h-full transition-all">
      
      {/* Step Header */}
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-sky-600 text-white font-bold text-xs flex items-center justify-center shadow-2xs">
            3
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base leading-tight">
              AI Explanation (Grad-CAM)
            </h2>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Visual attention heatmap on layer top_conv
            </p>
          </div>
        </div>
      </div>

      {/* Tabs & Guide Toggle */}
      <div className="px-5 pt-3 pb-2 flex items-center justify-between border-b border-slate-100 dark:border-slate-800">
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/80 p-1 rounded-xl">
          <button
            onClick={() => setActiveTab('original')}
            disabled={!gradcam}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              activeTab === 'original'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            Original
          </button>
          <button
            onClick={() => setActiveTab('attention')}
            disabled={!gradcam}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              activeTab === 'attention'
                ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-2xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            AI Attention
          </button>
          <button
            onClick={() => setActiveTab('overlay')}
            disabled={!gradcam}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all cursor-pointer ${
              activeTab === 'overlay'
                ? 'bg-white dark:bg-slate-700 text-sky-600 dark:text-sky-400 shadow-2xs'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            Overlay
          </button>
        </div>

        <button
          onClick={() => setShowExplanation(!showExplanation)}
          className="text-xs text-sky-600 dark:text-sky-400 hover:underline flex items-center gap-1 cursor-pointer font-medium"
        >
          <Info className="w-3.5 h-3.5" />
          <span>How to read this?</span>
        </button>
      </div>

      {/* Explanatory Collapsible Note */}
      {showExplanation && (
        <div className="px-5 py-3 bg-sky-50/70 dark:bg-sky-950/30 border-b border-sky-100 dark:border-sky-900/60 text-xs text-sky-950 dark:text-sky-200 leading-relaxed">
          <strong className="font-semibold text-sky-900 dark:text-sky-300">How to read this: </strong>
          Highlighted regions represent areas that contributed more strongly to the model&apos;s prediction. This visualization is provided for research interpretability and is not a clinical diagnostic tool.
        </div>
      )}

      {/* Main Image Display */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        {isLoading ? (
          <div className="flex-1 min-h-[260px] flex flex-col items-center justify-center text-center p-6">
            <Loader2 className="w-8 h-8 animate-spin text-sky-600 dark:text-sky-400 mb-2" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">
              Generating Grad-CAM heatmap...
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Extracting activation gradients from top_conv
            </p>
          </div>
        ) : !gradcam ? (
          <div className="flex-1 min-h-[260px] flex flex-col items-center justify-center text-center p-6 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/40 dark:bg-slate-850/20">
            <div className="w-12 h-12 rounded-full bg-white dark:bg-slate-800 text-slate-400 dark:text-slate-500 flex items-center justify-center mb-3 shadow-2xs border border-slate-200 dark:border-slate-700">
              <Layers className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Awaiting Model Analysis
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs leading-relaxed">
              Grad-CAM attention overlays will appear here once an MRI scan is analyzed.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            {/* Visualizer Frame */}
            <div className="relative w-full aspect-square max-h-[260px] bg-black/95 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 flex items-center justify-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={getImageSrc()!}
                alt={`Grad-CAM ${activeTab} visualization`}
                className="w-full h-full object-contain"
              />
              <div className="absolute bottom-2 left-2 px-2 py-0.5 bg-black/80 rounded text-[10px] text-white font-mono uppercase tracking-wider backdrop-blur-xs">
                Layer: {gradcam.target_layer} · View: {activeTab}
              </div>
            </div>

            <p className="mt-3 text-xs text-slate-500 dark:text-slate-400 text-center">
              Target class attribution: <strong className="text-slate-900 dark:text-white font-bold">{gradcam.prediction}</strong>
            </p>
          </div>
        )}

        {/* Subtle Card Footer */}
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span className="font-medium">Grad-CAM Interpretability Engine</span>
          <span className="flex items-center gap-1 text-sky-600 dark:text-sky-400 font-semibold">
            <Eye className="w-3.5 h-3.5" />
            Active
          </span>
        </div>

      </div>
    </div>
  );
}
