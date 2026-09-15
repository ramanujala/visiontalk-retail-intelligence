import { Store, StoreCreatePayload } from '../types/store';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchStores(token: string): Promise<Store[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stores`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error?.message || 'Failed to fetch stores.');
  }
  return data;
}

export async function createStore(token: string, payload: StoreCreatePayload): Promise<Store> {
  const res = await fetch(`${API_BASE_URL}/api/v1/stores`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.error?.message || 'Failed to create store.');
  }
  return data;
}
