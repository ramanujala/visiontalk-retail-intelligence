export interface LLMExplanationResponse {
  analysis_run_id: string;
  image_id: string;
  status: 'EXPLAINED' | 'FALLBACK' | 'FAILED';
  explanation: string;
  key_findings: string[];
  evidence_references: Record<string, any>;
  confidence: number;
  fallback_reason: string | null;
  model: string;
  created_at: string;
}
