'use client';

import React, { useState, useRef } from 'react';
import { X, AlertCircle } from 'lucide-react';
import HeroSection from '../components/HeroSection';
import UploadCard from '../components/UploadCard';
import ResultCard from '../components/ResultCard';
import GradcamViewer from '../components/GradcamViewer';
import SampleSelector from '../components/SampleSelector';
import ReportCard from '../components/ReportCard';
import BrainTumorInfo from '../components/BrainTumorInfo';
import ReportModal from '../components/ReportModal';
import InputValidationCard from '../components/InputValidationCard';
import { 
  analyzeImage, 
  analyzeSample, 
  getGradcam, 
  getGradcamForSample, 
  toDataUrl 
} from '../lib/api';
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
    setErrorMessage(null);
    setPrediction(null);
    setGradcam(null);

    const url = URL.createObjectURL(file);
    setPreviewUrl(url);

    // Auto-scroll to workspace
    workspaceRef.current?.scrollIntoView({ behavior: 'smooth' });

    // Auto-trigger analysis
    handleAnalyze(file);
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
    if (!file && !selectedSampleId) return;

    setIsAnalyzing(true);
    setIsGradcamLoading(true);
    setErrorMessage(null);

    try {
      let predResult: PredictionResponse;
      let gradcamResult: GradcamResponse | null = null;

      if (file && file.size > 0) {
        predResult = await analyzeImage(file);
        setPrediction(predResult);
        if (!predResult.is_withheld) {
          gradcamResult = await getGradcam(file, predResult.predicted_index);
          setGradcam(gradcamResult);
        } else {
          setGradcam(null);
        }
      } else if (selectedSampleId) {
        predResult = await analyzeSample(selectedSampleId);
        setPrediction(predResult);
        if (!predResult.is_withheld) {
          gradcamResult = await getGradcamForSample(selectedSampleId);
          setGradcam(gradcamResult);
        } else {
          setGradcam(null);
        }
      } else {
        return;
      }

      // Save to session-only history in localStorage
      const historyItem: HistoryItem = {
        id: predResult.analysis_id,
        prediction: predResult.prediction,
        confidence: predResult.confidence,
        timestamp: new Date().toISOString(),
        thumbnail: previewUrl || (gradcamResult ? toDataUrl(gradcamResult.original_image_base64) : ''),
        probabilities: predResult.probabilities,
        gradcam: gradcamResult || undefined,
      };

      try {
        const stored = localStorage.getItem('neuroscan_history');
        const historyList: HistoryItem[] = stored ? JSON.parse(stored) : [];
        historyList.unshift(historyItem);
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
    setPreviewUrl(sample.image_url);

    // Fetch the real sample image blob so selectedFile has actual image bytes
    fetch(sample.image_url)
      .then((r) => r.blob())
      .then((blob) => {
        setSelectedFile(new File([blob], sample.filename, { type: blob.type || 'image/jpeg' }));
      })
      .catch(() => {});

    // Scroll smoothly to workspace
    workspaceRef.current?.scrollIntoView({ behavior: 'smooth' });

    setIsAnalyzing(true);
    setIsGradcamLoading(true);

    try {
      // 1. Run real EfficientNet-B0 inference on the sample directly
      const predResult = await analyzeSample(sample.id);
      setPrediction(predResult);

      let gradcamResult: GradcamResponse | null = null;
      if (!predResult.is_withheld) {
        // 2. Run real Grad-CAM generation for the sample
        gradcamResult = await getGradcamForSample(sample.id);
        setGradcam(gradcamResult);
      } else {
        setGradcam(null);
      }

      // 3. Save to session-only history in localStorage
      const historyItem: HistoryItem = {
        id: predResult.analysis_id,
        prediction: predResult.prediction,
        confidence: predResult.confidence,
        timestamp: new Date().toISOString(),
        thumbnail: sample.image_url || (gradcamResult ? toDataUrl(gradcamResult.original_image_base64) : ''),
        probabilities: predResult.probabilities,
        gradcam: gradcamResult || undefined,
      };

      try {
        const stored = localStorage.getItem('neuroscan_history');
        const historyList: HistoryItem[] = stored ? JSON.parse(stored) : [];
        historyList.unshift(historyItem);
        localStorage.setItem('neuroscan_history', JSON.stringify(historyList.slice(0, 20)));
      } catch (err) {
        console.error('Failed to update session history:', err);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to analyze sample image.';
      setErrorMessage(msg);
    } finally {
      setIsAnalyzing(false);
      setIsGradcamLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* 1. Hero Section & Feature Strip */}
      <HeroSection
        onUploadClick={() => workspaceRef.current?.scrollIntoView({ behavior: 'smooth' })}
        onExampleClick={() => examplesRef.current?.scrollIntoView({ behavior: 'smooth' })}
      />

      {/* Dismissible Error Alert */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-200 text-sm flex items-center justify-between shadow-2xs">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
            <span><strong>Analysis Error:</strong> {errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="p-1 rounded-md text-rose-500 hover:text-rose-800 dark:hover:text-rose-200 cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 2. Input Validation Gate (Quality Check + OOD Detection) */}
      {(prediction?.validation || isAnalyzing) && (
        <InputValidationCard
          validation={prediction?.validation}
          isLoading={isAnalyzing}
        />
      )}

      {/* 3. Three-Step Analysis Workspace */}
      <section ref={workspaceRef} className="pt-2">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-stretch">
          
          {/* Step 1: Upload MRI Scan */}
          <UploadCard
            selectedFile={selectedFile}
            previewUrl={previewUrl}
            isLoading={isAnalyzing}
            onFileSelect={handleFileSelect}
            onRemove={handleRemove}
            onAnalyze={() => handleAnalyze()}
          />

          {/* Step 2: AI Analysis Result */}
          <ResultCard
            prediction={prediction}
            isLoading={isAnalyzing}
            onOpenReport={() => setIsReportOpen(true)}
          />

          {/* Step 3: AI Explanation (Grad-CAM) */}
          <GradcamViewer
            gradcam={gradcam}
            isLoading={isGradcamLoading}
          />

        </div>
      </section>

      {/* 4. Try an Example & Report Section */}
      <div ref={examplesRef} className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-8">
          <SampleSelector
            onSelectSample={handleSelectSample}
            isLoading={isAnalyzing}
            selectedSampleId={selectedSampleId}
          />
        </div>
        <div className="lg:col-span-4">
          <ReportCard
            onGenerateReport={() => setIsReportOpen(true)}
            hasAnalysis={prediction !== null}
          />
        </div>
      </div>

      {/* 5. Educational Brain Tumor Information */}
      <BrainTumorInfo />

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
