'use client';

import React from 'react';
import { 
  Sparkles, 
  Upload, 
  ArrowDown, 
  Cpu, 
  Eye, 
  Microscope, 
  ShieldCheck,
  Activity,
  ScanLine
} from 'lucide-react';

interface HeroSectionProps {
  onUploadClick: () => void;
  onExampleClick: () => void;
}

export default function HeroSection({ onUploadClick, onExampleClick }: HeroSectionProps) {
  return (
    <div className="space-y-6">
      {/* Two-Sided Hero Container */}
      <section className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 sm:p-8 lg:p-10 shadow-xs transition-colors">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          
          {/* Left Side: Content & Actions */}
          <div className="lg:col-span-7 space-y-4 text-left">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-400 text-xs font-semibold uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" />
              <span>BRAIN MRI ANALYSIS</span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-[44px] font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
              Advanced AI for <br className="hidden sm:inline" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 via-blue-600 to-indigo-600 dark:from-sky-400 dark:via-blue-400 dark:to-indigo-400">
                Better Brain Health
              </span>
            </h1>

            <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed max-w-xl">
              Upload a brain MRI scan and receive AI-assisted classification across four categories:{' '}
              <strong className="text-slate-800 dark:text-slate-100 font-semibold">No Tumor</strong>,{' '}
              <strong className="text-slate-800 dark:text-slate-100 font-semibold">Glioma Tumor</strong>,{' '}
              <strong className="text-slate-800 dark:text-slate-100 font-semibold">Meningioma Tumor</strong>, and{' '}
              <strong className="text-slate-800 dark:text-slate-100 font-semibold">Pituitary Tumor</strong>.
            </p>

            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={onUploadClick}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white shadow-xs shadow-sky-600/20 transition-all cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                <span>Upload MRI Scan</span>
              </button>
              <button
                onClick={onExampleClick}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-all cursor-pointer"
              >
                <ArrowDown className="w-4 h-4" />
                <span>Try an Example</span>
              </button>
            </div>
          </div>

          {/* Right Side: Clinical Brain/MRI Visual Graphic */}
          <div className="lg:col-span-5 flex items-center justify-center">
            <div className="relative w-full max-w-[360px] aspect-4/3 rounded-2xl bg-gradient-to-br from-sky-50 via-slate-50 to-blue-50/50 dark:from-slate-800/80 dark:via-slate-850 dark:to-slate-900 border border-sky-100 dark:border-slate-700/80 p-5 flex flex-col justify-between overflow-hidden shadow-xs">
              
              {/* Decorative Subtle Grid & Scanline */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,#0284c70a_1px,transparent_1px),linear-gradient(to_bottom,#0284c70a_1px,transparent_1px)] bg-[size:20px_20px]" />
              
              {/* Top Visual Header */}
              <div className="relative flex items-center justify-between z-10">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-sky-500 animate-pulse" />
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    Neural Diagnostic Map
                  </span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/80 dark:bg-slate-800 text-sky-700 dark:text-sky-300 border border-sky-200/60 dark:border-slate-700">
                  Res: 224×224×3
                </span>
              </div>

              {/* Center Abstract Brain Vector Graphic */}
              <div className="relative flex items-center justify-center py-2 z-10">
                <svg className="w-40 h-32 text-sky-600/80 dark:text-sky-400/80" viewBox="0 0 200 160" fill="none" xmlns="http://www.w3.org/2000/svg">
                  {/* Left Hemisphere Outline */}
                  <path d="M96 20 C60 20, 24 50, 24 90 C24 125, 55 140, 85 140 C92 140, 96 135, 96 125 Z" 
                        stroke="currentColor" strokeWidth="2.5" strokeDasharray="4 2" className="opacity-80" />
                  {/* Right Hemisphere Outline */}
                  <path d="M104 20 C140 20, 176 50, 176 90 C176 125, 145 140, 115 140 C108 140, 104 135, 104 125 Z" 
                        stroke="currentColor" strokeWidth="2.5" strokeDasharray="4 2" className="opacity-80" />
                  {/* Sulci and gyri lines */}
                  <path d="M45 60 Q70 70 85 55" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M155 60 Q130 70 115 55" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M35 95 Q65 105 88 90" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M165 95 Q135 105 112 90" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M55 125 Q75 120 90 115" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  <path d="M145 125 Q125 120 110 115" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  {/* Central fissure */}
                  <line x1="100" y1="20" x2="100" y2="135" stroke="currentColor" strokeWidth="2" strokeDasharray="3 3" />
                  {/* Focus focal nodes */}
                  <circle cx="65" cy="78" r="5" className="fill-sky-500 text-sky-500" />
                  <circle cx="135" cy="78" r="5" className="fill-blue-600 text-blue-600" />
                  <circle cx="100" cy="105" r="4" className="fill-teal-500 text-teal-500" />
                </svg>
              </div>

              {/* Bottom Visual Metrics Strip */}
              <div className="relative flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 z-10 pt-2 border-t border-slate-200/60 dark:border-slate-700/60">
                <span className="flex items-center gap-1">
                  <ScanLine className="w-3.5 h-3.5 text-sky-500" />
                  EfficientNet-B0 Backbone
                </span>
                <span className="font-mono text-slate-700 dark:text-slate-300 font-semibold">
                  Layer: top_conv
                </span>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* Feature Capability Strip */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-2xs">
          <div className="p-2 rounded-lg bg-sky-50 dark:bg-sky-950/70 text-sky-600 dark:text-sky-400 shrink-0">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
              AI-Powered Analysis
            </h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Deep CNN classification with fine-tuned EfficientNet-B0.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-2xs">
          <div className="p-2 rounded-lg bg-indigo-50 dark:bg-indigo-950/70 text-indigo-600 dark:text-indigo-400 shrink-0">
            <Eye className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
              Explainable AI
            </h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Grad-CAM attention overlays highlighting decision regions.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-2xs">
          <div className="p-2 rounded-lg bg-teal-50 dark:bg-teal-950/70 text-teal-600 dark:text-teal-400 shrink-0">
            <Microscope className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
              Research Focused
            </h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Benchmarked on 1,600 held-out clinical validation scans.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 shadow-2xs">
          <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-950/70 text-emerald-600 dark:text-emerald-400 shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white leading-tight">
              Input Validation
            </h4>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
              Pre-inference validation ensuring uploaded scans meet medical imaging standards.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
