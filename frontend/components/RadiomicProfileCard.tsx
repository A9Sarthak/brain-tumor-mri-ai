import React, { useState } from 'react';
import { Activity, MapPin, Compass, Maximize2, Shield, Eye, ScanLine } from 'lucide-react';
import { RadiomicBiomarkersResult } from '@/lib/types';
import { toDataUrl } from '@/lib/api';

interface RadiomicProfileCardProps {
  radiomics: RadiomicBiomarkersResult;
}

export default function RadiomicProfileCard({ radiomics }: RadiomicProfileCardProps) {
  const [showOverlay, setShowOverlay] = useState<boolean>(false);

  const isCircumscribed = radiomics.sphericity_index >= 0.65;
  const overlayUrl = radiomics.contour_overlay_base64 ? toDataUrl(radiomics.contour_overlay_base64) : null;

  return (
    <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-5 shadow-lg backdrop-blur">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Quantitative Radiomics & Morphometry
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono">
                Geometric Biomarkers
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Contour extraction, cross-sectional area, sphericity, and cranial compartment
            </p>
          </div>
        </div>

        {overlayUrl && (
          <button
            onClick={() => setShowOverlay(!showOverlay)}
            className={`px-2.5 py-1 text-xs font-medium rounded-lg border transition-all flex items-center gap-1.5 ${
              showOverlay
                ? 'bg-cyan-600 text-white border-cyan-500'
                : 'bg-slate-950 text-cyan-400 border-slate-800 hover:border-cyan-500/50'
            }`}
          >
            <ScanLine className="w-3.5 h-3.5" />
            {showOverlay ? 'Hide Contour' : 'View Contour Overlay'}
          </button>
        )}
      </div>

      {/* Contour Overlay Expanded Modal or Inline Viewer */}
      {showOverlay && overlayUrl && (
        <div className="mb-4 bg-slate-950 rounded-xl p-3 border border-cyan-500/30 flex flex-col items-center">
          <span className="text-xs font-medium text-cyan-300 mb-2 flex items-center gap-1.5">
            <ScanLine className="w-3.5 h-3.5" />
            Precision Lesion Margin Contour & Bounding Box Overlay
          </span>
          <div className="max-w-xs aspect-square rounded-lg overflow-hidden border border-cyan-500/40">
            <img src={overlayUrl} alt="Contour Overlay" className="w-full h-full object-cover" />
          </div>
        </div>
      )}

      {/* Anatomical Locus Banner */}
      <div className="mb-4 bg-slate-950/70 rounded-xl p-3 border border-slate-800/70 flex items-center gap-3">
        <div className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-cyan-400 shrink-0">
          <MapPin className="w-4 h-4" />
        </div>
        <div>
          <span className="text-[11px] uppercase tracking-wider text-slate-400 font-medium">
            Neuroanatomical Compartment
          </span>
          <p className="text-xs font-semibold text-slate-100">{radiomics.anatomical_locus}</p>
        </div>
      </div>

      {/* 4 Radiomic Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
        {/* Metric 1: Area */}
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
            <Maximize2 className="w-3.5 h-3.5 text-cyan-400" />
            Estimated Area
          </div>
          <div className="text-base font-bold text-slate-100 font-mono">
            {radiomics.estimated_area_mm2}{' '}
            <span className="text-[11px] font-normal text-slate-400">mm²</span>
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-0.5">
            {radiomics.estimated_area_pixels} px ({radiomics.slice_occupancy_pct}% slice)
          </div>
        </div>

        {/* Metric 2: Sphericity */}
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
            <Compass className="w-3.5 h-3.5 text-cyan-400" />
            Sphericity Index (Ψ)
          </div>
          <div className="text-base font-bold text-slate-100 font-mono">
            {radiomics.sphericity_index.toFixed(2)}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            <span className={`font-medium ${isCircumscribed ? 'text-emerald-400' : 'text-amber-400'}`}>
              {isCircumscribed ? '● Circumscribed' : '▲ Infiltrative'}
            </span>
          </div>
        </div>

        {/* Metric 3: Margin Irregularity */}
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Margin Roughness
          </div>
          <div className="text-base font-bold text-slate-100 font-mono">
            {radiomics.margin_irregularity.toFixed(2)}
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            {radiomics.margin_irregularity > 0.15 ? 'Jagged / Lobulated' : 'Smooth Boundary'}
          </div>
        </div>

        {/* Metric 4: Aspect Ratio */}
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            Aspect Ratio
          </div>
          <div className="text-base font-bold text-slate-100 font-mono">
            {radiomics.aspect_ratio.toFixed(2)}:1
          </div>
          <div className="text-[10px] text-slate-400 mt-0.5">
            Perimeter: {radiomics.perimeter_mm} mm
          </div>
        </div>
      </div>

      {/* Morphology Narrative Summary */}
      <div className="rounded-lg bg-slate-950/80 border border-slate-800/70 p-3 text-xs text-slate-300">
        <p className="font-medium text-slate-200 mb-0.5">Morphometric Profile:</p>
        <p className="text-slate-400 leading-relaxed">{radiomics.morphology_summary}</p>
      </div>
    </div>
  );
}

