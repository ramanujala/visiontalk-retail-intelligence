export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface DetectionItem {
  id: string;
  analysis_run_id: string;
  company_id: string;
  class_id: number;
  class_name: string;
  confidence: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  created_at: string;
}

export interface AnalysisRun {
  id: string;
  company_id: string;
  image_id: string;
  initiated_by: string;
  analysis_type: string;
  status: string;
  model_name: string;
  model_version: string;
  started_at: string;
  completed_at?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
  detections: DetectionItem[];
}

export interface AnalysisRunSummary {
  analysis_run_id: string;
  image_id: string;
  status: string;
  total_detections: number;
  detected_classes: string[];
  confidence_stats: {
    min: number;
    max: number;
    avg: number;
  };
  model_info: {
    model_name: string;
    model_version: string;
  };
}
