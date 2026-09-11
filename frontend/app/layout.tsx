import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '../components/ThemeProvider';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

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
      <body className="min-h-screen flex flex-col bg-[#f8fafc] dark:bg-[#090d16] text-slate-900 dark:text-slate-100 antialiased selection:bg-sky-500 selection:text-white transition-colors duration-150">
        <ThemeProvider>
          <Navbar />
          <main className="flex-1 max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
