import React, { useEffect, useState } from 'react';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Stores } from './pages/Stores';
import { HealthCard } from './components/HealthCard';
import { fetchLiveness, fetchReadiness } from './services/api';
import { fetchMe } from './services/auth';
import { LivenessStatus, ReadinessStatus } from './types/health';
import { User } from './types/auth';
import styles from './App.module.css';
import authStyles from './pages/Auth.module.css';

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('vt_token'));
  const [user, setUser] = useState<User | null>(null);
  const [authView, setAuthView] = useState<'login' | 'register'>('login');

  // System Health state
  const [liveness, setLiveness] = useState<LivenessStatus | null>(null);
  const [readiness, setReadiness] = useState<ReadinessStatus | null>(null);
  const [loadingHealth, setLoadingHealth] = useState<boolean>(true);
  const [healthError, setHealthError] = useState<string | null>(null);

  const checkHealth = async () => {
    setLoadingHealth(true);
    setHealthError(null);
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
      setHealthError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoadingHealth(false);
    }
  };

  const loadUserProfile = async (authToken: string) => {
    try {
      const profile = await fetchMe(authToken);
      setUser(profile);
    } catch (err) {
      // Invalid/expired token
      handleLogout();
    }
  };

  useEffect(() => {
    checkHealth();
    if (token) {
      loadUserProfile(token);
    }
  }, [token]);

  const handleLoginSuccess = (newToken: string) => {
    localStorage.setItem('vt_token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('vt_token');
    setToken(null);
    setUser(null);
  };

  return (
    <div className={styles.container}>
      <header className={styles.brandHeader}>
        <h1 className={styles.logo}>VisionTalk Retail Intelligence</h1>
        <p className={styles.tagline}>
          AI-Powered Retail Visual Intelligence Platform — Multi-Tenant Foundation
        </p>
      </header>

      {/* Authenticated Tenant Shell Header */}
      {token && user && (
        <div className={authStyles.tenantHeader} data-testid="tenant-header">
          <div className={authStyles.tenantInfo}>
            <div className={authStyles.companyBadge}>{user.company?.name || 'Company Tenant'}</div>
            <div className={authStyles.userBadge}>
              Logged in as: <strong>{user.full_name}</strong> ({user.email}) — Role: <strong>{user.role}</strong>
            </div>
          </div>
          <button className={authStyles.logoutBtn} onClick={handleLogout}>
            Logout
          </button>
        </div>
      )}

      {/* Auth Views vs Stores View */}
      {!token ? (
        authView === 'login' ? (
          <Login onSuccess={handleLoginSuccess} onSwitchToRegister={() => setAuthView('register')} />
        ) : (
          <Register onSuccess={handleLoginSuccess} onSwitchToLogin={() => setAuthView('login')} />
        )
      ) : (
        <Stores token={token} />
      )}

      {/* System Status Footnote Card */}
      <div style={{ marginTop: '3rem', width: '100%', display: 'flex', justifyContent: 'center' }}>
        <HealthCard
          liveness={liveness}
          readiness={readiness}
          loading={loadingHealth}
          error={healthError}
          onRefresh={checkHealth}
        />
      </div>
    </div>
  );
};

export default App;
