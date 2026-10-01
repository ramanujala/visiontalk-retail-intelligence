export interface ComplianceRule {
  id: string;
  company_id: string;
  store_id?: string;
  created_by: string;
  name: string;
  description?: string;
  rule_type: 'PRODUCT_REQUIRED' | 'PRODUCT_QUANTITY' | 'UNEXPECTED_PRODUCT' | 'PRODUCT_ZONE' | 'OCR_REQUIRED' | 'CUSTOM_THRESHOLD';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  configuration: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ComplianceRuleCreate {
  name: string;
  description?: string;
  rule_type: string;
  severity: string;
  configuration: Record<string, any>;
  is_active?: boolean;
  store_id?: string;
}

export interface ComplianceRuleUpdate {
  name?: string;
  description?: string;
  rule_type?: string;
  severity?: string;
  configuration?: Record<string, any>;
  is_active?: boolean;
  store_id?: string;
}

export interface ComplianceFinding {
  id: string;
  company_id: string;
  store_id: string;
  image_id: string;
  analysis_run_id: string;
  rule_id: string;
  status: 'PASS' | 'FAIL' | 'WARNING' | 'NOT_EVALUATED';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  details: Record<string, any>;
  evidence_references: any[];
  created_at: string;
}

export interface ComplianceSummaryResponse {
  image_id: string;
  analysis_run_id: string;
  total_rules: number;
  passed: number;
  failed: number;
  warnings: number;
  critical_findings: number;
  high_findings: number;
  medium_findings: number;
  low_findings: number;
  findings: ComplianceFinding[];
}

export interface ComplianceAnalysisRunResponse {
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
  compliance_findings: ComplianceFinding[];
}
