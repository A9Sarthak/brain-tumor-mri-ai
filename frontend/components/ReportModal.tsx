'use client';

import React, { useState } from 'react';
import { X, Printer, Copy, Check, ShieldAlert } from 'lucide-react';
import { PredictionResponse, GradcamResponse } from '../lib/types';
import { generateReport, toDataUrl } from '../lib/api';

interface ReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  prediction: PredictionResponse | null;
  gradcam: GradcamResponse | null;
  uploadedFileName?: string;
}

export default function ReportModal({
  isOpen,
  onClose,
  prediction,
  gradcam,
  uploadedFileName,
}: ReportModalProps) {
  const [copied, setCopied] = useState(false);
  const [reportText, setReportText] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  React.useEffect(() => {
    if (isOpen && prediction) {
      setIsGenerating(true);
      generateReport({
        analysis_id: prediction.analysis_id,
        prediction: prediction.prediction,
        confidence: prediction.confidence,
        probabilities: prediction.probabilities,
        image_filename: uploadedFileName,
      })
        .then((res) => {
          setReportText(res.report_text);
        })
        .catch((err) => {
          console.error(err);
        })
        .finally(() => {
          setIsGenerating(false);
        });
    }
  }, [isOpen, prediction, uploadedFileName]);

  if (!isOpen || !prediction) return null;

  const handleCopy = () => {
    if (reportText) {
      navigator.clipboard.writeText(reportText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden transition-colors">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 dark:text-white text-lg">
              Clinical Analysis Report
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Study ID: {prediction.analysis_id}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer text-xs flex items-center gap-1.5"
            >
              {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
            <button
              onClick={handlePrint}
              className="p-2 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors cursor-pointer text-xs flex items-center gap-1.5"
            >
              <Printer className="w-4 h-4" />
              <span>Print</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {/* Header Card */}
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div>
              <span className="text-[10px] uppercase font-bold text-sky-600 dark:text-sky-400 tracking-wider">
                NeuroScan AI Diagnostic Assistance
              </span>
              <h4 className="text-base font-bold text-slate-900 dark:text-white mt-0.5">
                Classification: {prediction.prediction}
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Confidence: {(prediction.confidence * 100).toFixed(2)}%
              </p>
            </div>
            <div className="text-right text-xs text-slate-400 font-mono">
              {new Date().toLocaleDateString()} {new Date().toLocaleTimeString()}
            </div>
          </div>

          {/* Visualization thumbnails */}
          {gradcam && (
            <div className="grid grid-cols-2 gap-4">
              <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-2 bg-slate-50 dark:bg-slate-800/40 text-center">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">
                  Original Scan
                </span>
                <div className="aspect-square bg-black rounded overflow-hidden flex items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={toDataUrl(gradcam.original_image_base64)}
                    alt="Original MRI"
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>
              <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-2 bg-slate-50 dark:bg-slate-800/40 text-center">
                <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400 block mb-1">
                  Grad-CAM Attention Overlay
                </span>
                <div className="aspect-square bg-black rounded overflow-hidden flex items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={toDataUrl(gradcam.overlay_image_base64)}
                    alt="Grad-CAM Overlay"
                    className="w-full h-full object-contain"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Full Plaintext Report */}
          <div className="space-y-2">
            <span className="text-xs uppercase font-semibold text-slate-500 dark:text-slate-400">
              Formatted Clinical Summary
            </span>
            <pre className="p-4 rounded-xl bg-slate-900 text-slate-200 text-xs font-mono overflow-x-auto whitespace-pre-wrap leading-relaxed border border-slate-800">
              {isGenerating ? 'Generating official summary...' : reportText}
            </pre>
          </div>

          {/* Responsible AI Disclaimer */}
          <div className="p-3.5 rounded-lg border border-amber-200 dark:border-amber-900/60 bg-amber-50 dark:bg-amber-950/20 text-xs text-amber-900 dark:text-amber-200/90 flex items-start gap-2.5">
            <ShieldAlert className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
            <div>
              <strong>Responsible AI Statement: </strong>
              NeuroScan AI outputs are generated by deep neural network models for academic and decision-support research. This report does NOT represent an official medical diagnosis.
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
