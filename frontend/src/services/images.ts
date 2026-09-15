import { ImageItem, ImageListResponse } from '../types/image';

const API_BASE_URL = '/api/v1';

export async function uploadImage(token: string, storeId: string, file: File): Promise<ImageItem> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('store_id', storeId);

  const response = await fetch(`${API_BASE_URL}/images`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload image.');
  }

  return response.json();
}

export async function fetchImages(token: string, storeId?: string): Promise<ImageListResponse> {
  let url = `${API_BASE_URL}/images?page=1&page_size=50`;
  if (storeId) {
    url += `&store_id=${encodeURIComponent(storeId)}`;
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch images.');
  }

  return response.json();
}

export async function deleteImage(token: string, imageId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/images/${imageId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to delete image.');
  }
}
