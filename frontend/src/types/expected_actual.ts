export interface ExpectedProduct {
  id: string;
  company_id: string;
  store_id: string;
  product_name: string;
  product_code: string;
  expected_quantity: number;
  expected_min_quantity: number;
  expected_max_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExpectedProductCreate {
  store_id: string;
  product_name: string;
  product_code: string;
  expected_quantity: number;
  expected_min_quantity: number;
  expected_max_quantity: number;
  is_active?: boolean;
}

export interface ExpectedProductUpdate {
  product_name?: string;
  product_code?: string;
  expected_quantity?: number;
  expected_min_quantity?: number;
  expected_max_quantity?: number;
  is_active?: boolean;
}

export interface ExpectedActualItem {
  id: string;
  analysis_run_id: string;
  company_id: string;
  expected_product_id?: string;
  product_code: string;
  product_name: string;
  expected_quantity: number;
  expected_min_quantity: number;
  expected_max_quantity: number;
  observed_quantity: number;
  difference: number;
  status: 'OBSERVED' | 'MISSING' | 'LOW_STOCK' | 'EXCESS' | 'UNEXPECTED' | 'UNMATCHED';
  evidence_references: any[];
  created_at: string;
}

export interface ExpectedActualIssue {
  id: string;
  analysis_run_id: string;
  company_id: string;
  store_id: string;
  image_id: string;
  expected_product_id?: string;
  issue_type: 'MISSING_PRODUCT' | 'LOW_STOCK' | 'EXCESS_PRODUCT' | 'UNEXPECTED_PRODUCT' | 'UNMATCHED_OBSERVATION';
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  message: string;
  evidence_references: any[];
  created_at: string;
}

export interface ExpectedActualAnalysisRunResponse {
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
  expected_actual_items: ExpectedActualItem[];
  expected_actual_issues: ExpectedActualIssue[];
}
