import React from 'react';
import { LivenessStatus, ReadinessStatus } from '../types/health';
import styles from './HealthCard.module.css';

interface HealthCardProps {
  liveness: LivenessStatus | null;
  readiness: ReadinessStatus | null;
  loading: boolean;
  error: string | null;
  onRefresh: () => void;
}

export const HealthCard: React.FC<HealthCardProps> = ({
  liveness,
  readiness,
  loading,
  error,
  onRefresh,
}) => {
  return (
    <div className={styles.card} data-testid="health-card">
      <div className={styles.cardHeader}>
        <h2 className={styles.title}>System Status & Health Check</h2>
      </div>

      {loading ? (
        <p style={{ color: 'var(--text-secondary)' }}>Checking backend services...</p>
      ) : error ? (
        <div className={styles.statusRow}>
          <span className={styles.label}>Backend Connection</span>
          <span className={`${styles.badge} ${styles.badgeError}`}>
            <span className={styles.dot} />
            Disconnected
          </span>
        </div>
      ) : (
        <div className={styles.statusGroup}>
          <div className={styles.statusRow}>
            <span className={styles.label}>Application Liveness</span>
            <span className={`${styles.badge} ${liveness?.status === 'healthy' ? styles.badgeSuccess : styles.badgeError}`}>
              <span className={styles.dot} />
              {liveness?.status || 'Unknown'}
            </span>
          </div>

          <div className={styles.statusRow}>
            <span className={styles.label}>PostgreSQL Readiness</span>
            <span className={`${styles.badge} ${readiness?.database_connected ? styles.badgeSuccess : styles.badgeError}`}>
              <span className={styles.dot} />
              {readiness?.database_connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      )}

      <button className={styles.refreshButton} onClick={onRefresh} disabled={loading}>
        {loading ? 'Refreshing...' : 'Re-check Status'}
      </button>
    </div>
  );
};
