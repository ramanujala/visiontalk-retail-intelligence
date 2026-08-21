import React, { useEffect, useState } from 'react';
import { HealthCard } from './components/HealthCard';
import { fetchLiveness, fetchReadiness } from './services/api';
import { LivenessStatus, ReadinessStatus } from './types/health';
import styles from './App.module.css';

export const App: React.FC = () => {
  const [liveness, setLiveness] = useState<LivenessStatus | null>(null);
  const [readiness, setReadiness] = useState<ReadinessStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const liveData = await fetchLiveness();
      setLiveness(liveData);
      try {
        const readyData = await fetchReadiness();
        setReadiness(readyData);
      } catch (readyErr) {
        setReadiness({
          status: 'unhealthy',
          database_connected: false,
          version: liveData.version,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className={styles.container}>
      <header className={styles.brandHeader}>
        <h1 className={styles.logo}>VisionTalk Retail Intelligence</h1>
        <p className={styles.tagline}>
          AI-Powered Retail Visual Intelligence Platform — Project Foundation Shell
        </p>
      </header>

      <HealthCard
        liveness={liveness}
        readiness={readiness}
        loading={loading}
        error={error}
        onRefresh={checkHealth}
      />
    </div>
  );
};

export default App;
