import { 
  PredictionResponse, 
  GradcamResponse, 
  PerformanceResponse, 
  SampleItem, 
  ReportResponse 
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export async function checkHealth(): Promise<{
  status: string;
  model_loaded: boolean;
  model_name: string;
  input_shape: (number | null)[];
  num_classes: number;
  classes: string[];
}> {
  const res = await fetch(`${API_BASE_URL}/api/health`);
  if (!res.ok) {
    throw new Error(`API health check failed with status: ${res.status}`);
  }
  return res.json();
}

export async function analyzeImage(file: File): Promise<PredictionResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to analyze image' }));
    throw new Error(errorData.detail || `Analysis failed: ${res.statusText}`);
  }

  return res.json();
}

export async function getGradcam(file: File, targetClassIdx?: number): Promise<GradcamResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  let url = `${API_BASE_URL}/api/gradcam`;
  if (targetClassIdx !== undefined && targetClassIdx !== null) {
    url += `?target_class_idx=${targetClassIdx}`;
  }

  const res = await fetch(url, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to generate Grad-CAM' }));
    throw new Error(errorData.detail || `Grad-CAM failed: ${res.statusText}`);
  }

  return res.json();
}

export async function getPerformance(): Promise<PerformanceResponse> {
  const res = await fetch(`${API_BASE_URL}/api/performance`);
  if (!res.ok) {
    throw new Error(`Failed to load model performance metrics: ${res.statusText}`);
  }
  return res.json();
}

export async function getSamples(): Promise<SampleItem[]> {
  const res = await fetch(`${API_BASE_URL}/api/samples`);
  if (!res.ok) {
    throw new Error(`Failed to fetch sample scans: ${res.statusText}`);
  }
  const samples: SampleItem[] = await res.json();
  // Ensure image_url is absolute if relative
  return samples.map(s => ({
    ...s,
    image_url: s.image_url.startsWith('http') ? s.image_url : `${API_BASE_URL}${s.image_url}`
  }));
}

export async function fetchSampleAsFile(sample: SampleItem): Promise<File> {
  const res = await fetch(sample.image_url);
  if (!res.ok) {
    throw new Error(`Failed to download sample image: ${res.statusText}`);
  }
  const blob = await res.blob();
  return new File([blob], sample.filename, { type: blob.type || 'image/jpeg' });
}

export async function generateReport(params: {
  analysis_id: string;
  prediction: string;
  confidence: number;
  probabilities: Record<string, number>;
  image_filename?: string;
  clinical_notes?: string;
}): Promise<ReportResponse> {
  const res = await fetch(`${API_BASE_URL}/api/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      analysis_id: params.analysis_id,
      prediction: params.prediction,
      confidence: params.confidence,
      probabilities: params.probabilities,
      image_filename: params.image_filename || 'mri_scan.jpg',
      clinical_notes: params.clinical_notes || '',
    }),
  });

  if (!res.ok) {
    throw new Error(`Failed to generate clinical report: ${res.statusText}`);
  }

  return res.json();
}
