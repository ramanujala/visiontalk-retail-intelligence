import { LLMExplanationResponse } from '../types/llm';

const API_BASE = '/api/v1';

export const fetchImageExplanation = async (
  token: string,
  imageId: string,
  forceReanalyze: boolean = false,
  questionContext?: string
): Promise<LLMExplanationResponse> => {
  const response = await fetch(`${API_BASE}/llm/explain/${imageId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      force_reanalyze: forceReanalyze,
      question_context: questionContext || null
    })
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}));
    throw new Error(errData.detail || 'Failed to generate LLM explanation.');
  }

  return response.json();
};
