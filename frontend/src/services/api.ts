import { LivenessStatus, ReadinessStatus } from '../types/health';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchLiveness(): Promise<LivenessStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`);
  if (!response.ok) {
    throw new Error(`Liveness check failed with status ${response.status}`);
  }
  return response.json();
}

export async function fetchReadiness(): Promise<ReadinessStatus> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health/ready`);
  if (!response.ok && response.status !== 530 && response.status !== 503) {
    throw new Error(`Readiness check failed with status ${response.status}`);
  }
  return response.json();
}
