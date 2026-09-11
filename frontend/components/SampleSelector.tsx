'use client';

import React, { useEffect, useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';
import { SampleItem } from '../lib/types';
import { getSamples } from '../lib/api';

interface SampleSelectorProps {
  onSelectSample: (sample: SampleItem) => void;
  isLoading: boolean;
  selectedSampleId?: string | null;
}

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
    <section className="mt-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-xs transition-colors">
      <div className="flex items-center justify-between mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            <h3 className="text-base font-semibold text-slate-900 dark:text-white">
              Try an Example
            </h3>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Explore the analysis workflow using representative MRI scans.
          </p>
        </div>
      </div>

      {loadingSamples ? (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-sky-600 dark:text-sky-400" />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {samples.map((sample) => {
            const isSelected = selectedSampleId === sample.id;
            return (
              <button
                key={sample.id}
                onClick={() => onSelectSample(sample)}
                disabled={isLoading}
                className={`group relative rounded-xl border p-3 text-left transition-all cursor-pointer flex flex-col items-center ${
                  isSelected
                    ? 'border-sky-500 bg-sky-50/60 dark:bg-sky-950/40 ring-2 ring-sky-500/20'
                    : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 hover:border-sky-300 dark:hover:border-slate-700 hover:shadow-xs'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {/* Image Thumbnail */}
                <div className="w-full aspect-square bg-black rounded-lg overflow-hidden mb-2.5 flex items-center justify-center">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={sample.image_url}
                    alt={sample.display_name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                </div>

                <div className="w-full text-center">
                  <span className="block text-xs font-semibold text-slate-800 dark:text-slate-200 truncate">
                    {sample.display_name}
                  </span>
                  <span className="block text-[10px] text-slate-400 dark:text-slate-500 font-mono truncate">
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
