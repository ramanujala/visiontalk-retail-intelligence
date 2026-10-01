import {
  ExpectedProduct,
  ExpectedProductCreate,
  ExpectedProductUpdate,
  ExpectedActualAnalysisRunResponse
} from '../types/expected_actual';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const fetchExpectedProducts = async (
  token: string,
  storeId?: string,
  isActive?: boolean
): Promise<ExpectedProduct[]> => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  if (isActive !== undefined) params.append('is_active', String(isActive));

  const response = await fetch(`${API_BASE_URL}/expected-products?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to fetch expected products');
  }

  return response.json();
};

export const createExpectedProduct = async (
  token: string,
  payload: ExpectedProductCreate
): Promise<ExpectedProduct> => {
  const response = await fetch(`${API_BASE_URL}/expected-products`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to create expected product');
  }

  return response.json();
};

export const updateExpectedProduct = async (
  token: string,
  productId: string,
  payload: ExpectedProductUpdate
): Promise<ExpectedProduct> => {
  const response = await fetch(`${API_BASE_URL}/expected-products/${productId}`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to update expected product');
  }

  return response.json();
};

export const deleteExpectedProduct = async (
  token: string,
  productId: string
): Promise<void> => {
  const response = await fetch(`${API_BASE_URL}/expected-products/${productId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to delete expected product');
  }
};

export const runExpectedVsActualAnalysis = async (
  token: string,
  imageId: string,
  forceReanalyze: boolean = false
): Promise<ExpectedActualAnalysisRunResponse> => {
  const response = await fetch(
    `${API_BASE_URL}/analysis/expected-vs-actual/${imageId}?force_reanalyze=${forceReanalyze}`,
    {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error?.message || err.detail || 'Failed to run Expected vs Actual analysis');
  }

  return response.json();
};
