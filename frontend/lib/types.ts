export interface QualityChecks {
  readable: boolean;
  dimensions: boolean;
  brightness: boolean;
  contrast: boolean;
  sharpness: boolean;
}

export interface QualityResult {
  status: 'good' | 'fair' | 'poor' | 'rejected';
  score: number;
  warnings: string[];
  checks: QualityChecks;
  metrics?: Record<string, any>;
}

export interface OODResult {
  status: 'in_distribution' | 'uncertain' | 'out_of_distribution';
  score: number;
  warning?: string | null;
  metrics?: Record<string, any>;
}

export interface ValidationResult {
  quality: QualityResult;
  ood: OODResult;
  is_acceptable: boolean;
  action: 'proceed' | 'withhold' | 'reject';
  reason?: string | null;
}

export interface PredictionResponse {
  analysis_id: string;
  prediction: string;
  predicted_index: number;
  confidence: number;
  probabilities: Record<string, number>;
  processing_time_ms: number;
  validation?: ValidationResult;
  is_withheld?: boolean;
  withheld_reason?: string | null;
}

export interface GradcamResponse {
  analysis_id: string;
  prediction: string;
  original_image_base64: string;
  attention_heatmap_base64: string;
  overlay_image_base64: string;
  target_layer: string;
}

export interface PerformanceResponse {
  model_name: string;
  architecture: string;
  test_sample_count: number;
  accuracy: number;
  precision_macro: number;
  precision_weighted: number;
  recall_macro: number;
  recall_weighted: number;
  f1_macro: number;
  f1_weighted: number;
  prediction_distribution: Record<string, number>;
  per_class_report: Record<string, {
    precision: number;
    recall: number;
    'f1-score': number;
    support: number;
  }>;
  confusion_matrix_url: string;
  accuracy_plot_url: string;
  loss_plot_url: string;
  training_history: {
    accuracy?: number[];
    val_accuracy?: number[];
    loss?: number[];
    val_loss?: number[];
  };
}

export interface SampleItem {
  id: string;
  class_name: string;
  display_name: string;
  filename: string;
  image_url: string;
}

export interface ReportResponse {
  analysis_id: string;
  report_text: string;
  generated_at: string;
}

export interface HistoryItem {
  id: string;
  prediction: string;
  confidence: number;
  timestamp: string;
  thumbnail: string;
  probabilities: Record<string, number>;
  gradcam?: GradcamResponse;
}
