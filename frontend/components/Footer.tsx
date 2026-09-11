'use client';

import React from 'react';
import Link from 'next/link';
import { Activity } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/60 mt-16 transition-colors">
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          
          {/* Left: Brand & Tagline */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-sky-600 dark:bg-sky-500 flex items-center justify-center text-white shadow-xs">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold tracking-wider text-slate-900 dark:text-white text-sm">
                  NEUROSCAN
                </span>
                <span className="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded bg-sky-100 dark:bg-sky-950/70 text-sky-700 dark:text-sky-400 border border-sky-200 dark:border-sky-800">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400">
                AI for a Healthier Tomorrow
              </p>
            </div>
          </div>

          {/* Center: Legal & Links */}
          <div className="flex items-center gap-6 text-xs text-slate-500 dark:text-slate-400">
            <Link href="/about" className="hover:text-slate-900 dark:hover:text-white transition-colors">
              About
            </Link>
            <Link href="/insights" className="hover:text-slate-900 dark:hover:text-white transition-colors">
              Model Insights
            </Link>
            <span className="hover:text-slate-900 dark:hover:text-white cursor-pointer transition-colors">
              Privacy &amp; Data Governance
            </span>
            <span className="hover:text-slate-900 dark:hover:text-white cursor-pointer transition-colors">
              Terms of Research Use
            </span>
          </div>

          {/* Right: Lineage & Copyright */}
          <div className="text-right text-xs text-slate-400 dark:text-slate-500">
            <p>© {new Date().getFullYear()} NeuroScan AI · Research Prototype</p>
            <p className="text-[11px] text-slate-400/80 dark:text-slate-500 mt-0.5">
              Powered by EfficientNet-B0 &amp; Grad-CAM
            </p>
          </div>

        </div>
      </div>
    </footer>
  );
}
