import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '../components/ThemeProvider';
import Navbar from '../components/Navbar';

export const metadata: Metadata = {
  title: 'NeuroScan AI — Clinical Brain MRI Analysis & Interpretability',
  description: 'AI-assisted brain MRI scan classification across four categories with Grad-CAM visual explanations.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 antialiased selection:bg-sky-500 selection:text-white transition-colors duration-150">
        <ThemeProvider>
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {children}
          </main>
          <footer className="border-t border-slate-200 dark:border-slate-800/80 py-6 bg-white dark:bg-slate-900/50 text-center text-xs text-slate-500 dark:text-slate-400 transition-colors">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
              <p>© {new Date().getFullYear()} NeuroScan AI Medical Platform. Research prototype.</p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500">
                Powered by EfficientNet-B0 &amp; Grad-CAM Interpretability Engine
              </p>
            </div>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
