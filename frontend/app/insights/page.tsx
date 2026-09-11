'use client';

import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  CheckCircle2, 
  Activity, 
  TrendingUp, 
  Layers, 
  HelpCircle,
  Loader2,
  FileCheck
} from 'lucide-react';
import { getPerformance } from '../../lib/api';
import { PerformanceResponse } from '../../lib/types';
import DisclaimerBanner from '../../components/DisclaimerBanner';

export default function InsightsPage() {
  const [metrics, setMetrics] = useState<PerformanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPerformance()
      .then((data) => {
        setMetrics(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load performance metrics');
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-sky-600 dark:text-sky-400" />
        <p className="text-sm text-slate-500 dark:text-slate-400">Loading model evaluation metrics...</p>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="p-6 rounded-xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-200">
        Failed to load evaluation data: {error}
      </div>
    );
  }

  const kpis = [
    {
      label: 'Test Accuracy',
      value: `${(metrics.accuracy * 100).toFixed(2)}%`,
      desc: 'Held-out test evaluation',
      icon: CheckCircle2,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-950/50',
    },
    {
      label: 'Macro Precision',
      value: `${(metrics.precision_macro * 100).toFixed(2)}%`,
      desc: 'Balanced across all classes',
      icon: Activity,
      color: 'text-sky-600 dark:text-sky-400',
      bg: 'bg-sky-50 dark:bg-sky-950/50',
    },
    {
      label: 'Macro Recall',
      value: `${(metrics.recall_macro * 100).toFixed(2)}%`,
      desc: 'Sensitivity rate',
      icon: TrendingUp,
      color: 'text-indigo-600 dark:text-indigo-400',
      bg: 'bg-indigo-50 dark:bg-indigo-950/50',
    },
    {
      label: 'Macro F1-Score',
      value: `${(metrics.f1_macro * 100).toFixed(2)}%`,
      desc: 'Harmonic mean of P & R',
      icon: Layers,
      color: 'text-teal-600 dark:text-teal-400',
      bg: 'bg-teal-50 dark:bg-teal-950/50',
    },
  ];

  return (
    <div className="space-y-8">
      <DisclaimerBanner />

      {/* Page Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-400 text-xs font-semibold uppercase tracking-wider mb-2">
          <BarChart3 className="w-3.5 h-3.5" />
          <span>MODEL BENCHMARKS</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
          Model Insights
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Performance on held-out test data ({metrics.test_sample_count.toLocaleString()} verified MRI scans)
        </p>
      </div>

      {/* Metrics Distinction Alert */}
      <div className="p-4 rounded-xl bg-sky-50/50 dark:bg-sky-950/20 border border-sky-200 dark:border-sky-900/50 flex items-start gap-3 text-xs text-sky-900 dark:text-sky-200">
        <FileCheck className="w-5 h-5 text-sky-600 dark:text-sky-400 shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold">Rigorous Evaluation Protocol: </strong>
          The metrics displayed below reflect performance strictly on the uncorrupted, held-out test split of 1,600 MRI scans. Validation metrics during two-stage transfer learning reached ~91% on augmented validation sets, while final generalization on unseen clinical test images remains locked at 80.00% accuracy.
        </div>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xs transition-colors"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  {kpi.label}
                </span>
                <div className={`p-2 rounded-lg ${kpi.bg} ${kpi.color}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
              <div className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white font-mono">
                {kpi.value}
              </div>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1">
                {kpi.desc}
              </p>
            </div>
          );
        })}
      </div>

      {/* Per-Class Performance Table */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white">
            Per-Class Performance
          </h2>
          <span className="text-xs text-slate-400">Classification Report Breakdown</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-600 dark:text-slate-300 font-semibold border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-6 py-3">Class</th>
                <th className="px-6 py-3">Precision</th>
                <th className="px-6 py-3">Recall</th>
                <th className="px-6 py-3">F1-Score</th>
                <th className="px-6 py-3">Test Support</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 text-slate-700 dark:text-slate-300">
              {Object.entries(metrics.per_class_report)
                .filter(([k]) => ['No Tumor', 'Glioma Tumor', 'Meningioma Tumor', 'Pituitary Tumor'].includes(k))
                .map(([name, stat]) => (
                  <tr key={name} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                    <td className="px-6 py-3 font-semibold text-slate-900 dark:text-white">{name}</td>
                    <td className="px-6 py-3 font-mono">{(stat.precision * 100).toFixed(1)}%</td>
                    <td className="px-6 py-3 font-mono">{(stat.recall * 100).toFixed(1)}%</td>
                    <td className="px-6 py-3 font-mono font-medium text-sky-600 dark:text-sky-400">
                      {(stat['f1-score'] * 100).toFixed(1)}%
                    </td>
                    <td className="px-6 py-3 font-mono text-slate-500">{stat.support} scans</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Evaluation Artifacts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Confusion Matrix */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white">
              Confusion Matrix
            </h2>
            <span className="text-xs text-slate-400">1,600 test scans</span>
          </div>
          <div className="aspect-square bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center p-2 border border-slate-800">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`http://127.0.0.1:8000${metrics.confusion_matrix_url}`}
              alt="Test Confusion Matrix"
              className="max-h-full max-w-full object-contain"
            />
          </div>
          <p className="mt-3 text-xs text-slate-500 dark:text-slate-400">
            Normalized diagonal represents true positive rate per MRI category.
          </p>
        </div>

        {/* Training History Curves */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Training History
              </h2>
              <span className="text-xs text-slate-400">Accuracy &amp; Loss</span>
            </div>
            
            <div className="space-y-4">
              <div className="aspect-video bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center p-2 border border-slate-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`http://127.0.0.1:8000${metrics.accuracy_plot_url}`}
                  alt="Training Accuracy Curve"
                  className="max-h-full max-w-full object-contain"
                />
              </div>

              <div className="aspect-video bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center p-2 border border-slate-800">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={`http://127.0.0.1:8000${metrics.loss_plot_url}`}
                  alt="Training Loss Curve"
                  className="max-h-full max-w-full object-contain"
                />
              </div>
            </div>
          </div>

          <p className="mt-4 text-xs text-slate-500 dark:text-slate-400">
            Two-stage training curves illustrating backbone warm-up followed by fine-tuning of top convolutional blocks.
          </p>
        </div>

      </div>

    </div>
  );
}
