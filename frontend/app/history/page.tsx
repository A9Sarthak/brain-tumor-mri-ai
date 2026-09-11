'use client';

import React, { useEffect, useState } from 'react';
import { 
  History as HistoryIcon, 
  Trash2, 
  Eye, 
  Calendar, 
  FileText, 
  Layers,
  ArrowRight
} from 'lucide-react';
import { HistoryItem } from '../../lib/types';
import { toDataUrl } from '../../lib/api';
import DisclaimerBanner from '../../components/DisclaimerBanner';
import ReportModal from '../../components/ReportModal';

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<HistoryItem | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('neuroscan_history');
      if (stored) {
        setHistory(JSON.parse(stored));
      }
    } catch (err) {
      console.error('Error loading history:', err);
    }
  }, []);

  const handleClearHistory = () => {
    if (confirm('Clear all session analysis history? This action cannot be undone.')) {
      localStorage.removeItem('neuroscan_history');
      setHistory([]);
      setSelectedItem(null);
    }
  };

  return (
    <div className="space-y-8">
      <DisclaimerBanner />

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-5">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <HistoryIcon className="w-3.5 h-3.5" />
            <span>SESSION ARCHIVE</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white">
            Analysis History
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Review analyses performed during the current browsing session.
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="self-start sm:self-auto flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 hover:bg-rose-100 dark:hover:bg-rose-900/60 transition-colors cursor-pointer"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear History</span>
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <div className="p-12 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-white dark:bg-slate-900/50">
          <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400 mx-auto flex items-center justify-center mb-3">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-1">
            No Session Analyses Found
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto mb-4">
            Scans analyzed in the workspace will appear here during your current session. No patient data is stored permanently on remote servers.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {history.map((item) => (
            <div
              key={item.id}
              className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-xs hover:border-sky-300 dark:hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                {/* Thumbnail */}
                <div className="relative aspect-video bg-black flex items-center justify-center overflow-hidden border-b border-slate-100 dark:border-slate-800">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={toDataUrl(item.thumbnail)}
                    alt={item.prediction}
                    className="w-full h-full object-contain"
                  />
                  <span className="absolute top-2 right-2 px-2 py-0.5 rounded text-[10px] font-mono bg-black/75 text-white backdrop-blur-xs">
                    {(item.confidence * 100).toFixed(1)}% Conf
                  </span>
                </div>

                {/* Details */}
                <div className="p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs uppercase font-bold text-sky-600 dark:text-sky-400">
                      Prediction
                    </span>
                    <span className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                      <Calendar className="w-3 h-3" />
                      {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 dark:text-white">
                    {item.prediction}
                  </h3>

                  <div className="pt-2">
                    <div className="text-[11px] text-slate-500 dark:text-slate-400 mb-1 font-medium">
                      Top Class Probabilities
                    </div>
                    <div className="space-y-1">
                      {Object.entries(item.probabilities).map(([name, prob]) => (
                        <div key={name} className="flex justify-between text-[11px]">
                          <span className="text-slate-600 dark:text-slate-400 truncate">{name}</span>
                          <span className="font-mono text-slate-800 dark:text-slate-200">
                            {(prob * 100).toFixed(1)}%
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="p-4 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => {
                    setSelectedItem(item);
                    setIsReportOpen(true);
                  }}
                  className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 transition-colors cursor-pointer"
                >
                  <FileText className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
                  <span>View Report</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Report Modal */}
      {selectedItem && (
        <ReportModal
          isOpen={isReportOpen}
          onClose={() => {
            setIsReportOpen(false);
            setSelectedItem(null);
          }}
          prediction={{
            analysis_id: selectedItem.id,
            prediction: selectedItem.prediction,
            confidence: selectedItem.confidence,
            probabilities: selectedItem.probabilities,
            predicted_index: 0,
            processing_time_ms: 0,
          }}
          gradcam={selectedItem.gradcam || null}
          uploadedFileName="Archived Scan"
        />
      )}
    </div>
  );
}
