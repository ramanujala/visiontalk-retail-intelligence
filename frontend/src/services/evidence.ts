import { CanonicalEvidenceResponse } from '../types/evidence';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const fetchCanonicalEvidence = async (
  token: string,
  imageId: string,
  forceRegenerate: boolean = false
): Promise<CanonicalEvidenceResponse> => {
  const endpoint = forceRegenerate
    ? `${API_BASE_URL}/evidence/generate/${imageId}`
    : `${API_BASE_URL}/evidence/image/${imageId}`;

  const method = forceRegenerate ? 'POST' : 'GET';

  const response = await fetch(endpoint, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.error?.message || errorData.detail || 'Failed to fetch canonical evidence';
    throw new Error(message);
  }

  return response.json();
};
