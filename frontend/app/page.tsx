'use client';

import React, { useState, useRef } from 'react';
import { 
  Sparkles, 
  Cpu, 
  Eye, 
  Microscope, 
  HeartHandshake, 
  ArrowDown, 
  Upload
} from 'lucide-react';
import UploadCard from '../components/UploadCard';
import ResultCard from '../components/ResultCard';
import GradcamViewer from '../components/GradcamViewer';
import SampleSelector from '../components/SampleSelector';
import ReportModal from '../components/ReportModal';
import DisclaimerBanner from '../components/DisclaimerBanner';
import { analyzeImage, getGradcam, fetchSampleAsFile } from '../lib/api';
import { PredictionResponse, GradcamResponse, SampleItem, HistoryItem } from '../lib/types';

export default function AnalyzePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [selectedSampleId, setSelectedSampleId] = useState<string | null>(null);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isGradcamLoading, setIsGradcamLoading] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [gradcam, setGradcam] = useState<GradcamResponse | null>(null);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const workspaceRef = useRef<HTMLDivElement>(null);
  const examplesRef = useRef<HTMLDivElement>(null);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setSelectedSampleId(null);
    setPrediction(null);
    setGradcam(null);
    setErrorMessage(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target?.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemove = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setSelectedSampleId(null);
    setPrediction(null);
    setGradcam(null);
    setErrorMessage(null);
  };

  const handleAnalyze = async (fileToAnalyze?: File) => {
    const file = fileToAnalyze || selectedFile;
    if (!file) return;

    setIsAnalyzing(true);
    setIsGradcamLoading(true);
    setErrorMessage(null);

    try {
      // 1. Run real EfficientNet-B0 inference
      const predResult = await analyzeImage(file);
      setPrediction(predResult);

      // 2. Run real Grad-CAM generation
      const gradcamResult = await getGradcam(file, predResult.predicted_index);
      setGradcam(gradcamResult);

      // 3. Save to session-only history in localStorage
      const historyItem: HistoryItem = {
        id: predResult.analysis_id,
        prediction: predResult.prediction,
        confidence: predResult.confidence,
        timestamp: new Date().toISOString(),
        thumbnail: previewUrl || `data:image/png;base64,${gradcamResult.original_image_base64}`,
        probabilities: predResult.probabilities,
        gradcam: gradcamResult,
      };

      try {
        const stored = localStorage.getItem('neuroscan_history');
        const historyList: HistoryItem[] = stored ? JSON.parse(stored) : [];
        historyList.unshift(historyItem);
        // Keep max 20 session items
        localStorage.setItem('neuroscan_history', JSON.stringify(historyList.slice(0, 20)));
      } catch (err) {
        console.error('Failed to update session history:', err);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'An error occurred during MRI analysis.';
      setErrorMessage(msg);
    } finally {
      setIsAnalyzing(false);
      setIsGradcamLoading(false);
    }
  };

  const handleSelectSample = async (sample: SampleItem) => {
    setSelectedSampleId(sample.id);
    setErrorMessage(null);
    setPrediction(null);
    setGradcam(null);

    try {
      const file = await fetchSampleAsFile(sample);
      setSelectedFile(file);
      setPreviewUrl(sample.image_url);

      // Scroll smoothly to workspace
      workspaceRef.current?.scrollIntoView({ behavior: 'smooth' });

      // Automatically trigger real analysis and Grad-CAM
      await handleAnalyze(file);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load sample image.';
      setErrorMessage(msg);
    }
  };

  return (
    <div className="space-y-8">
      
      {/* Medical Disclaimer Banner */}
      <DisclaimerBanner />

      {/* Hero Section */}
      <section className="text-center py-6 sm:py-10 max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-50 dark:bg-sky-950/60 border border-sky-200 dark:border-sky-800 text-sky-700 dark:text-sky-400 text-xs font-semibold uppercase tracking-wider">
          <Sparkles className="w-3.5 h-3.5" />
          <span>BRAIN MRI ANALYSIS</span>
        </div>

        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Advanced AI for <br className="hidden sm:inline" />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-blue-600 dark:from-sky-400 dark:to-blue-400">
            Better Brain Health
          </span>
        </h1>

        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 leading-relaxed max-w-2xl mx-auto">
          Upload a brain MRI scan and receive AI-assisted classification across four categories:
          <strong className="text-slate-800 dark:text-slate-100 font-semibold"> No Tumor</strong>,
          <strong className="text-slate-800 dark:text-slate-100 font-semibold"> Glioma Tumor</strong>,
          <strong className="text-slate-800 dark:text-slate-100 font-semibold"> Meningioma Tumor</strong>, and
          <strong className="text-slate-800 dark:text-slate-100 font-semibold"> Pituitary Tumor</strong>.
        </p>

        {/* CTAs */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            onClick={() => workspaceRef.current?.scrollIntoView({ behavior: 'smooth' })}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white shadow-sm shadow-sky-600/20 transition-colors cursor-pointer"
          >
            <Upload className="w-4 h-4" />
            <span>Upload MRI Scan</span>
          </button>
          <button
            onClick={() => examplesRef.current?.scrollIntoView({ behavior: 'smooth' })}
            className="flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-750 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 transition-colors cursor-pointer"
          >
            <ArrowDown className="w-4 h-4" />
            <span>Try an Example</span>
          </button>
        </div>
      </section>

      {/* Feature Highlights Row */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3 max-w-5xl mx-auto">
        <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs">
          <div className="p-1.5 rounded-lg bg-sky-50 dark:bg-sky-950 text-sky-600 dark:text-sky-400">
            <Cpu className="w-4 h-4" />
          </div>
          <span className="font-medium">AI-Powered Analysis</span>
        </div>

        <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs">
          <div className="p-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400">
            <Eye className="w-4 h-4" />
          </div>
          <span className="font-medium">Explainable AI</span>
        </div>

        <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs">
          <div className="p-1.5 rounded-lg bg-teal-50 dark:bg-teal-950 text-teal-600 dark:text-teal-400">
            <Microscope className="w-4 h-4" />
          </div>
          <span className="font-medium">Research Focused</span>
        </div>

        <div className="flex items-center gap-2.5 p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 text-xs">
          <div className="p-1.5 rounded-lg bg-rose-50 dark:bg-rose-950 text-rose-600 dark:text-rose-400">
            <HeartHandshake className="w-4 h-4" />
          </div>
          <span className="font-medium">Towards Better Brain Health</span>
        </div>
      </section>

      {/* Error alert if any */}
      {errorMessage && (
        <div className="max-w-5xl mx-auto p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-200 text-sm">
          <strong>Analysis Error: </strong> {errorMessage}
        </div>
      )}

      {/* Main 3-Part Clinical Workspace */}
      <section ref={workspaceRef} className="max-w-7xl mx-auto pt-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          
          {/* 1. Upload Card */}
          <UploadCard
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            isLoading={isAnalyzing}
            onFileSelect={handleFileSelect}
            onRemove={handleRemove}
            onAnalyze={() => handleAnalyze()}
          />

          {/* 2. Analysis Result Card */}
          <ResultCard
            prediction={prediction}
            isLoading={isAnalyzing}
            onOpenReport={() => setIsReportOpen(true)}
          />

          {/* 3. Grad-CAM Card */}
          <GradcamViewer
            gradcam={gradcam}
            isLoading={isGradcamLoading}
          />

        </div>
      </section>

      {/* Try an Example Section */}
      <div ref={examplesRef}>
        <SampleSelector
          onSelectSample={handleSelectSample}
          isLoading={isAnalyzing}
          selectedSampleId={selectedSampleId}
        />
      </div>

      {/* Report Modal */}
      <ReportModal
        isOpen={isReportOpen}
        onClose={() => setIsReportOpen(false)}
        prediction={prediction}
        gradcam={gradcam}
        uploadedFileName={selectedFile?.name}
      />

    </div>
  );
}
