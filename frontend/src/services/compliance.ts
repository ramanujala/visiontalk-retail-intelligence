import {
  ComplianceRule,
  ComplianceRuleCreate,
  ComplianceRuleUpdate,
  ComplianceAnalysisRunResponse,
  ComplianceSummaryResponse,
  ComplianceFinding
} from '../types/compliance';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const fetchComplianceRules = async (
  token: string,
  storeId?: string,
  isActive?: boolean
): Promise<ComplianceRule[]> => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  if (isActive !== undefined) params.append('is_active', String(isActive));

  const response = await fetch(`${API_BASE_URL}/compliance-rules?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to fetch compliance rules');
  }

  return response.json();
};

export const createComplianceRule = async (
  token: string,
  payload: ComplianceRuleCreate
): Promise<ComplianceRule> => {
  const response = await fetch(`${API_BASE_URL}/compliance-rules`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to create compliance rule');
  }

  return response.json();
};

export const updateComplianceRule = async (
  token: string,
  ruleId: string,
  payload: ComplianceRuleUpdate
): Promise<ComplianceRule> => {
  const response = await fetch(`${API_BASE_URL}/compliance-rules/${ruleId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to update compliance rule');
  }

  return response.json();
};

export const deleteComplianceRule = async (
  token: string,
  ruleId: string
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/compliance-rules/${ruleId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to delete compliance rule');
  }
};

export const executeComplianceAnalysis = async (
  token: string,
  imageId: string,
  forceReanalyze: boolean = false
): Promise<ComplianceAnalysisRunResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/compliance/analyze/${imageId}?force_reanalyze=${forceReanalyze}`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to execute compliance analysis');
  }

  return response.json();
};

export const fetchComplianceSummary = async (
  token: string,
  imageId: string
): Promise<ComplianceSummaryResponse> => {
  const response = await fetch(`${API_BASE_URL}/compliance/image/${imageId}/summary`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to fetch compliance summary');
  }

  return response.json();
};
