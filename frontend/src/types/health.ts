export interface LivenessStatus {
  status: string;
  version: string;
  timestamp: string;
}

export interface ReadinessStatus {
  status: string;
  database_connected: bool;
  version: string;
  timestamp: string;
}

export interface SystemHealthState {
  liveness: LivenessStatus | null;
  readiness: ReadinessStatus | null;
  loading: boolean;
  error: string | null;
}
