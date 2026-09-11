'use client';

import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, X, ArrowRight, Loader2, CheckCircle2 } from 'lucide-react';

interface UploadCardProps {
  selectedFile: File | null;
  previewUrl: string | null;
  isLoading: boolean;
  onFileSelect: (file: File) => void;
  onRemove: () => void;
  onAnalyze: () => void;
}

export default function UploadCard({
  selectedFile,
  previewUrl,
  isLoading,
  onFileSelect,
  onRemove,
  onAnalyze,
}: UploadCardProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndHandleFile = (file: File) => {
    setErrorMsg(null);
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png)$/i)) {
      setErrorMsg('Unsupported format. Please upload a JPG or PNG MRI scan.');
      return;
    }
    if (file.size > 200 * 1024 * 1024) {
      setErrorMsg('File exceeds 200MB size limit.');
      return;
    }
    onFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndHandleFile(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200/90 dark:border-slate-800 rounded-2xl shadow-xs overflow-hidden flex flex-col h-full transition-all">
      
      {/* Step Header */}
      <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-full bg-sky-600 text-white font-bold text-xs flex items-center justify-center shadow-2xs">
            1
          </div>
          <div>
            <h2 className="font-bold text-slate-900 dark:text-white text-sm sm:text-base leading-tight">
              Upload MRI Scan
            </h2>
            <p className="text-[11px] text-slate-400 dark:text-slate-500">
              Select or drop brain imaging scan
            </p>
          </div>
        </div>
        <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400">
          JPG / PNG · Max 200MB
        </span>
      </div>

      {/* Card Content */}
      <div className="p-5 flex-1 flex flex-col justify-between">
        {!previewUrl ? (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center min-h-[260px] ${
              isDragOver
                ? 'border-sky-500 bg-sky-50/80 dark:bg-sky-950/40'
                : 'border-sky-200/80 dark:border-slate-700 bg-sky-50/30 dark:bg-slate-800/30 hover:border-sky-400 hover:bg-sky-50/60 dark:hover:bg-slate-800/50'
            }`}
          >
            <div className="w-12 h-12 rounded-full bg-white dark:bg-slate-800 text-sky-600 dark:text-sky-400 flex items-center justify-center mb-3 shadow-2xs border border-sky-100 dark:border-slate-700">
              <UploadCloud className="w-6 h-6" />
            </div>
            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 mb-0.5">
              Drag &amp; drop an MRI image here
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              or click to browse from local workstation
            </p>
            <span className="inline-flex items-center px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-white dark:bg-slate-800 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-slate-700 shadow-2xs hover:bg-sky-50 transition-colors">
              Select MRI File
            </span>
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,image/jpeg,image/png"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  validateAndHandleFile(e.target.files[0]);
                }
              }}
            />
          </div>
        ) : (
          <div className="flex flex-col gap-3.5">
            {/* Image Preview Box */}
            <div className="relative w-full aspect-square max-h-[260px] bg-black/95 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 flex items-center justify-center group">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={previewUrl}
                alt="MRI Scan Preview"
                className="w-full h-full object-contain"
              />
              <button
                onClick={onRemove}
                disabled={isLoading}
                aria-label="Remove scan"
                className="absolute top-2.5 right-2.5 p-1.5 rounded-full bg-slate-900/80 hover:bg-rose-600 text-white transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
              
              <div className="absolute bottom-2 left-2 px-2 py-0.5 bg-black/75 rounded text-[10px] text-emerald-400 font-medium flex items-center gap-1 backdrop-blur-xs">
                <CheckCircle2 className="w-3 h-3" />
                <span>Ready for analysis</span>
              </div>
            </div>

            {/* File Details */}
            {selectedFile && (
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-xs">
                <div className="flex items-center gap-2 truncate">
                  <FileText className="w-4 h-4 text-sky-600 dark:text-sky-400 shrink-0" />
                  <span className="truncate font-medium text-slate-800 dark:text-slate-200">
                    {selectedFile.name}
                  </span>
                </div>
                {selectedFile.size > 0 && (
                  <span className="text-slate-500 dark:text-slate-400 shrink-0 ml-2 font-mono">
                    {formatFileSize(selectedFile.size)}
                  </span>
                )}
              </div>
            )}
          </div>
        )}

        {errorMsg && (
          <p className="mt-2 text-xs text-rose-600 dark:text-rose-400 font-medium">
            {errorMsg}
          </p>
        )}

        {/* Action Controls */}
        <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center gap-3">
          {previewUrl && (
            <button
              onClick={onRemove}
              disabled={isLoading}
              className="px-3 py-2 text-xs font-medium text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors cursor-pointer"
            >
              Remove
            </button>
          )}

          <button
            onClick={onAnalyze}
            disabled={(!selectedFile && !previewUrl) || isLoading}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all cursor-pointer shadow-xs ${
              (!selectedFile && !previewUrl) || isLoading
                ? 'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed border border-slate-200 dark:border-slate-700'
                : 'bg-sky-600 hover:bg-sky-700 active:bg-sky-800 text-white shadow-sky-600/20'
            }`}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin text-white" />
                <span>Analyzing MRI...</span>
              </>
            ) : (
              <>
                <span>Analyze Image</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
