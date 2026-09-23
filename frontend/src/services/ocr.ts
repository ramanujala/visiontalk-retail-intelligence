import { OCRAnalysisRun, OCRSummary } from '../types/ocr';

const API_BASE_URL = '/api/v1';

export async function analyzeImageText(token: string, imageId: string, forceReanalyze: boolean = false): Promise<OCRAnalysisRun> {
  const url = `${API_BASE_URL}/ocr/analyze/${imageId}${forceReanalyze ? '?force_reanalyze=true' : ''}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'OCR text extraction failed.');
  }

  return response.json();
}

export async function fetchOCRAnalysisRun(token: string, analysisRunId: string): Promise<OCRAnalysisRun> {
  const response = await fetch(`${API_BASE_URL}/ocr/${analysisRunId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch OCR analysis run details.');
  }

  return response.json();
}

export async function fetchImageOCRAnalysisRuns(token: string, imageId: string): Promise<OCRAnalysisRun[]> {
  const response = await fetch(`${API_BASE_URL}/ocr/image/${imageId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch image OCR analysis runs.');
  }

  return response.json();
}

export async function fetchOCRAnalysisRunSummary(token: string, analysisRunId: string): Promise<OCRSummary> {
  const response = await fetch(`${API_BASE_URL}/ocr/${analysisRunId}/summary`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch OCR analysis run summary.');
  }

  return response.json();
}
