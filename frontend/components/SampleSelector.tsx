'use client';

import React, { useEffect, useState } from 'react';
import { Sparkles, Loader2, ArrowUpRight } from 'lucide-react';
import { SampleItem } from '../lib/types';
import { getSamples } from '../lib/api';

interface SampleSelectorProps {
  onSelectSample: (sample: SampleItem) => void;
  isLoading: boolean;
  selectedSampleId?: string | null;
}

const SAMPLE_DESCRIPTIONS: Record<string, string> = {
  notumor: 'Normal brain MRI',
  glioma: 'Representative MRI sample',
  meningioma: 'Representative MRI sample',
  pituitary: 'Representative MRI sample',
};

export default function SampleSelector({
  onSelectSample,
  isLoading,
  selectedSampleId,
}: SampleSelectorProps) {
  const [samples, setSamples] = useState<SampleItem[]>([]);
  const [loadingSamples, setLoadingSamples] = useState(true);

  useEffect(() => {
    getSamples()
      .then((data) => {
        setSamples(data);
        setLoadingSamples(false);
      })
      .catch((err) => {
        console.error('Failed to load samples:', err);
        setLoadingSamples(false);
      });
  }, []);

  return (
    <section className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl p-6 sm:p-7 shadow-xs transition-colors">
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            <h3 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white">
              Try an Example
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Explore the analysis workflow using representative MRI scans. Click any sample to run AI inference.
          </p>
        </div>
      </div>

      {loadingSamples ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-sky-600 dark:text-sky-400" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {samples.map((sample) => {
            const isSelected = selectedSampleId === sample.id;
            const description = SAMPLE_DESCRIPTIONS[sample.id] || 'Representative MRI sample';

            return (
              <button
                key={sample.id}
                onClick={() => onSelectSample(sample)}
                disabled={isLoading}
                className={`group relative rounded-xl border p-3.5 text-left transition-all cursor-pointer flex flex-col justify-between ${
                  isSelected
                    ? 'border-sky-500 bg-sky-50/70 dark:bg-sky-950/40 ring-2 ring-sky-500/20 shadow-xs'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 hover:border-sky-300 dark:hover:border-slate-700 hover:shadow-xs hover:bg-white dark:hover:bg-slate-800/60'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {/* Image Thumbnail */}
                <div className="relative w-full aspect-square bg-black rounded-lg overflow-hidden mb-3 flex items-center justify-center border border-slate-200/60 dark:border-slate-700/60">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={sample.image_url}
                    alt={sample.display_name}
                    className="w-full h-full object-cover group-hover:scale-103 transition-transform duration-300"
                  />
                  <span className="absolute top-2 right-2 p-1 rounded-full bg-slate-900/70 text-white group-hover:bg-sky-600 transition-colors">
                    <ArrowUpRight className="w-3 h-3" />
                  </span>
                </div>

                <div className="w-full">
                  <div className="flex items-center justify-between">
                    <span className="block text-xs font-bold text-slate-900 dark:text-white truncate">
                      {sample.display_name}
                    </span>
                  </div>
                  <span className="block text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                    {description}
                  </span>
                  <span className="block text-[10px] text-slate-400 font-mono mt-1">
                    {sample.filename}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </section>
  );
}
