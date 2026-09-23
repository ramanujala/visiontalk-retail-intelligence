export interface OCRResultItem {
  id: string;
  analysis_run_id: string;
  company_id: string;
  text: string;
  normalized_text: string;
  confidence: number;
  line_order: number;
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
  created_at: string;
}

export interface OCRAnalysisRun {
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
  ocr_results: OCRResultItem[];
}

export interface OCRSummary {
  analysis_run_id: string;
  image_id: string;
  status: string;
  total_regions: number;
  confidence_stats: {
    min: number;
    max: number;
    avg: number;
  };
  extracted_text_sample: string[];
  model_info: {
    model_name: string;
    model_version: string;
  };
}
