import React from 'react';
import { ShieldCheck, AlertTriangle, HelpCircle, Layers, CheckCircle2 } from 'lucide-react';
import { ConformalPredictionResult } from '@/lib/types';

interface ConformalSetCardProps {
  conformal: ConformalPredictionResult;
}

export default function ConformalSetCard({ conformal }: ConformalSetCardProps) {
  const isSingleton = conformal.is_singleton;
  const uncertaintyPct = Math.round(conformal.epistemic_uncertainty_score * 100);

  // Status colors
  const statusColor = isSingleton
    ? 'text-emerald-400 bg-emerald-950/40 border-emerald-800/60'
    : conformal.set_size === 2
    ? 'text-amber-400 bg-amber-950/40 border-amber-800/60'
    : 'text-rose-400 bg-rose-950/40 border-rose-800/60';

  return (
    <div className="bg-slate-900/90 rounded-xl border border-slate-800 p-5 shadow-lg backdrop-blur">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
              Conformal Prediction Set
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono">
                1 - α = 95%
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Distribution-free finite-sample statistical coverage guarantee
            </p>
          </div>
        </div>

        <div className={`px-2.5 py-1 rounded-full text-xs font-medium border flex items-center gap-1.5 ${statusColor}`}>
          {isSingleton ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Singleton (Resolved)</span>
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{conformal.ambiguity_status}</span>
            </>
          )}
        </div>
      </div>

      {/* Main Prediction Set Chips */}
      <div className="mb-4">
        <div className="text-xs font-medium text-slate-400 mb-2 flex items-center justify-between">
          <span>95% Confidence Differential Set:</span>
          <span className="text-[11px] text-slate-400 font-mono">
            Cardinality: |Ĉ| = {conformal.set_size}
          </span>
        </div>

        <div className="flex flex-wrap gap-2">
          {conformal.prediction_set_95.map((className, idx) => (
            <div
              key={idx}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-2 border shadow-sm ${
                idx === 0
                  ? 'bg-indigo-600/20 text-indigo-200 border-indigo-500/40'
                  : 'bg-amber-500/15 text-amber-200 border-amber-500/30'
              }`}
            >
              <Layers className="w-3.5 h-3.5 opacity-75" />
              {className}
              {idx === 0 && (
                <span className="text-[10px] uppercase tracking-wider bg-indigo-500/30 px-1.5 py-0.2 rounded font-mono text-indigo-200">
                  Primary
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Epistemic Uncertainty & Entropy Gauges */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
            <span>Epistemic Uncertainty</span>
            <span className="font-mono font-semibold text-slate-200">{uncertaintyPct}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                uncertaintyPct < 25
                  ? 'bg-emerald-500'
                  : uncertaintyPct < 55
                  ? 'bg-amber-500'
                  : 'bg-rose-500'
              }`}
              style={{ width: `${uncertaintyPct}%` }}
            />
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/60">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5">
            <span>Shannon Entropy H(p)</span>
            <span className="font-mono font-semibold text-slate-200">
              {conformal.shannon_entropy.toFixed(3)}
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div
              className="h-full bg-indigo-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.round(conformal.normalized_entropy * 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Clinical Guidance Note */}
      <div className="rounded-lg bg-slate-950/80 border border-slate-800/70 p-3 text-xs text-slate-300 flex items-start gap-2.5">
        <HelpCircle className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <p className="font-medium text-slate-200 mb-0.5">Clinical Protocol Guidance:</p>
          <p className="text-slate-400 leading-relaxed">{conformal.clinical_recommendation}</p>
        </div>
      </div>
    </div>
  );
}

