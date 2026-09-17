import { AnalysisRun, AnalysisRunSummary } from '../types/detection';

const API_BASE_URL = '/api/v1';

export async function analyzeImage(token: string, imageId: string, forceReanalyze: boolean = false): Promise<AnalysisRun> {
  const url = `${API_BASE_URL}/detections/analyze/${imageId}${forceReanalyze ? '?force_reanalyze=true' : ''}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Object detection analysis failed.');
  }

  return response.json();
}

export async function fetchAnalysisRun(token: string, analysisRunId: string): Promise<AnalysisRun> {
  const response = await fetch(`${API_BASE_URL}/detections/${analysisRunId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch analysis run details.');
  }

  return response.json();
}

export async function fetchImageAnalysisRuns(token: string, imageId: string): Promise<AnalysisRun[]> {
  const response = await fetch(`${API_BASE_URL}/detections/image/${imageId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch image analysis runs.');
  }

  return response.json();
}

export async function fetchAnalysisRunSummary(token: string, analysisRunId: string): Promise<AnalysisRunSummary> {
  const response = await fetch(`${API_BASE_URL}/detections/${analysisRunId}/summary`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch analysis run summary.');
  }

  return response.json();
}
