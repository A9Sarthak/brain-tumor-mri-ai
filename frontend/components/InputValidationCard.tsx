'use client';

import React from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  AlertOctagon, 
  ShieldCheck, 
  Info,
  Maximize2,
  Sun,
  Contrast,
  Focus
} from 'lucide-react';
import { ValidationResult } from '../lib/types';

interface InputValidationCardProps {
  validation: ValidationResult | null | undefined;
  isLoading?: boolean;
}

export default function InputValidationCard({ validation, isLoading }: InputValidationCardProps) {
  if (isLoading) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 shadow-xs animate-pulse space-y-3">
        <div className="h-4 w-36 bg-slate-200 dark:bg-slate-800 rounded"></div>
        <div className="grid grid-cols-3 gap-3">
          <div className="h-10 bg-slate-100 dark:bg-slate-800/60 rounded-lg"></div>
          <div className="h-10 bg-slate-100 dark:bg-slate-800/60 rounded-lg"></div>
          <div className="h-10 bg-slate-100 dark:bg-slate-800/60 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!validation) return null;

  const { quality, ood } = validation;

  const qualityLabel = quality.status.charAt(0).toUpperCase() + quality.status.slice(1);
  const isQualityGood = quality.status === 'good';
  const isQualityFair = quality.status === 'fair';
  const isQualityPoor = quality.status === 'poor';
  const isQualityRejected = quality.status === 'rejected';

  const isOOD = ood.status === 'out_of_distribution';
  const isUncertain = ood.status === 'uncertain';
  const isInDistribution = ood.status === 'in_distribution';

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-5 sm:p-6 shadow-xs space-y-4 transition-colors">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/60 pb-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-md bg-sky-50 dark:bg-sky-950/70 text-sky-600 dark:text-sky-400">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs uppercase font-bold tracking-wider text-slate-800 dark:text-slate-200">
              Input Validation
            </h3>
            <p className="text-[11px] text-slate-400">
              Technical quality audit &amp; out-of-distribution detection
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {validation.is_acceptable ? (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Input Accepted</span>
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60">
              <AlertOctagon className="w-3.5 h-3.5" />
              <span>Classification Withheld</span>
            </span>
          )}
        </div>
      </div>

      {/* Validation Checklist Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        
        {/* 1. Image Readability */}
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/60">
          <CheckCircle2 className={`w-4 h-4 shrink-0 ${quality.checks.readable ? 'text-emerald-500' : 'text-rose-500'}`} />
          <div className="min-w-0">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">File Integrity</span>
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate block">
              {quality.checks.readable ? 'Image readable' : 'Corrupted / Unreadable'}
            </span>
          </div>
        </div>

        {/* 2. Image Quality */}
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/60">
          {isQualityGood && <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />}
          {(isQualityFair || isQualityPoor) && <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500" />}
          {isQualityRejected && <AlertOctagon className="w-4 h-4 shrink-0 text-rose-500" />}
          <div className="min-w-0">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Quality Status</span>
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate block">
              Image quality: {qualityLabel} ({quality.score}/100)
            </span>
          </div>
        </div>

        {/* 3. Input Distribution */}
        <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200/80 dark:border-slate-700/60">
          {isInDistribution && <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-500" />}
          {isUncertain && <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500" />}
          {isOOD && <AlertOctagon className="w-4 h-4 shrink-0 text-rose-500" />}
          <div className="min-w-0">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Domain Distribution</span>
            <span className="text-xs font-semibold text-slate-800 dark:text-slate-200 truncate block">
              {isInDistribution && 'Input distribution: Consistent'}
              {isUncertain && 'Input distribution: Uncertain'}
              {isOOD && 'Input distribution: Out-of-Distribution'}
            </span>
          </div>
        </div>

      </div>

      {/* Quality Warnings (if any) */}
      {quality.warnings.length > 0 && !isQualityRejected && (
        <div className="p-3 rounded-xl bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/50 text-amber-900 dark:text-amber-200/90 text-xs flex items-start gap-2.5">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="font-semibold block">Image Quality Warning:</strong>
            {quality.warnings.map((w, idx) => (
              <p key={idx} className="leading-relaxed text-[11px] sm:text-xs">{w}</p>
            ))}
            <p className="text-[10px] text-amber-700 dark:text-amber-400/80 italic pt-0.5">
              The image can still be analyzed, but image quality may affect reliability.
            </p>
          </div>
        </div>
      )}

      {/* OOD Alert (if Out of Distribution) */}
      {isOOD && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-900 dark:text-rose-200 text-xs flex items-start gap-3">
          <AlertOctagon className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="text-sm font-bold block text-rose-700 dark:text-rose-300">
              Input Outside Expected Distribution
            </strong>
            <p className="text-xs leading-relaxed text-rose-800 dark:text-rose-200/90">
              This image appears substantially different from the MRI data used by this model. A reliable classification cannot be provided.
            </p>
          </div>
        </div>
      )}

      {/* Quality Rejected Alert */}
      {isQualityRejected && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-900 dark:text-rose-200 text-xs flex items-start gap-3">
          <AlertOctagon className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="text-sm font-bold block text-rose-700 dark:text-rose-300">
              Unusable Image Content
            </strong>
            <p className="text-xs leading-relaxed text-rose-800 dark:text-rose-200/90">
              {quality.warnings[0] || 'The uploaded file failed technical quality inspection and cannot be analyzed.'}
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
