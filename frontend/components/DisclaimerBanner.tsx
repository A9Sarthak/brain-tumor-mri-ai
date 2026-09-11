import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function DisclaimerBanner() {
  return (
    <div className="rounded-lg border border-amber-200 dark:border-amber-900/60 bg-amber-50/70 dark:bg-amber-950/30 p-3 sm:p-3.5 text-amber-900 dark:text-amber-200/90 text-xs sm:text-sm flex items-start gap-2.5 transition-colors">
      <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" />
      <div className="leading-relaxed">
        <strong className="font-semibold text-amber-950 dark:text-amber-200">Clinical Research Notice: </strong>
        NeuroScan AI is an academic/research prototype for brain MRI image classification. It is not a certified medical device and should not be used as a substitute for professional clinical medical diagnosis. Always consult a licensed healthcare practitioner for patient evaluation.
      </div>
    </div>
  );
}
