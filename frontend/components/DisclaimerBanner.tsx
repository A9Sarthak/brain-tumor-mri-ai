import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="rounded-xl border border-amber-200/80 dark:border-amber-900/50 bg-[#fffdfa] dark:bg-amber-950/20 p-3 sm:p-3.5 text-xs text-amber-900/90 dark:text-amber-200/90 flex items-start gap-2.5 transition-colors shadow-2xs">
      <div className="p-1 rounded-md bg-amber-100 dark:bg-amber-900/40 text-amber-700 dark:text-amber-300 shrink-0 mt-0.5">
        <AlertTriangle className="w-3.5 h-3.5" />
      </div>
      <div className="leading-relaxed">
        <span className="font-semibold text-amber-950 dark:text-amber-200">Clinical Research Notice: </span>
        NeuroScan AI is an academic and research prototype for automated brain MRI analysis. It is not a certified medical diagnostic device and must not replace professional clinical diagnosis. Always consult a qualified medical physician or radiologist.
      </div>
    </div>
  );
}
