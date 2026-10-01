import React, { useEffect, useState } from 'react';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Stores } from './pages/Stores';
import { ImageUpload } from './pages/ImageUpload';
import { ObjectDetectionView } from './pages/ObjectDetectionView';
import { OCRView } from './pages/OCRView';
import { EvidenceView } from './pages/EvidenceView';
import { ExpectedActualView } from './pages/ExpectedActualView';
import { ComplianceView } from './pages/ComplianceView';
import { ExpectedProductManager } from './components/ExpectedProductManager';
import { ComplianceRuleManager } from './components/ComplianceRuleManager';
import { HealthCard } from './components/HealthCard';
import { fetchLiveness, fetchReadiness } from './services/api';
import { fetchMe } from './services/auth';
import { fetchStores } from './services/stores';
import { LivenessStatus, ReadinessStatus } from './types/health';
import { User } from './types/auth';
import { Store } from './types/store';
import { ImageItem } from './types/image';
import styles from './App.module.css';
import authStyles from './pages/Auth.module.css';

export const App: React.FC = () => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('vt_token'));
  const [user, setUser] = useState<User | null>(null);
  const [stores, setStores] = useState<Store[]>([]);
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState<'stores' | 'images' | 'detection' | 'ocr' | 'evidence' | 'expected_actual' | 'planogram' | 'compliance_rules' | 'compliance'>('images');
  const [selectedImageForAnalysis, setSelectedImageForAnalysis] = useState<ImageItem | null>(null);

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
          timestamp: new Date().toISOString(),
          checks: { postgresql: 'disconnected' }
        });
      }
    } catch (err: any) {
      setHealthError(err.message || 'Failed to connect to backend service.');
    } finally {
      setLoadingHealth(false);
    }
  };

  const loadUserProfileAndStores = async (authToken: string) => {
    try {
      const profile = await fetchMe(authToken);
      setUser(profile);
      const storeList = await fetchStores(authToken);
      setStores(storeList);
    } catch (err) {
      // Invalid/expired token
      handleLogout();
    }
  };

  useEffect(() => {
    checkHealth();
    if (token) {
      loadUserProfileAndStores(token);
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
    setStores([]);
  };

  const handleSelectImageForAnalysis = (img: ImageItem) => {
    setSelectedImageForAnalysis(img);
    setActiveTab('detection');
  };

  const handleSelectImageForOCR = (img: ImageItem) => {
    setSelectedImageForAnalysis(img);
    setActiveTab('ocr');
  };

  const handleSelectImageForEvidence = (img: ImageItem) => {
    setSelectedImageForAnalysis(img);
    setActiveTab('evidence');
  };

  const handleSelectImageForExpectedActual = (img: ImageItem) => {
    setSelectedImageForAnalysis(img);
    setActiveTab('expected_actual');
  };

  const handleSelectImageForCompliance = (img: ImageItem) => {
    setSelectedImageForAnalysis(img);
    setActiveTab('compliance');
  };

  return (
    <div className={styles.container}>
      <header className={styles.brandHeader}>
        <h1 className={styles.logo}>VisionTalk Retail Intelligence</h1>
        <p className={styles.tagline}>
          AI-Powered Retail Visual Intelligence Platform — Perception Layer (YOLO + PaddleOCR)
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

      {/* Navigation Tabs when Authenticated */}
      {token && user && (
        <div style={{ display: 'flex', gap: '1rem', width: '100%', maxWidth: '800px', margin: '0 auto 1.5rem auto' }}>
          <button
            onClick={() => setActiveTab('images')}
            style={{
              flex: 1,
              padding: '0.8rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'images' ? 'var(--primary-color, #3b82f6)' : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Image Ingestion & Gallery
          </button>
          <button
            onClick={() => setActiveTab('stores')}
            style={{
              flex: 1,
              padding: '0.8rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'stores' ? 'var(--primary-color, #3b82f6)' : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Store Locations
          </button>
          <button
            onClick={() => setActiveTab('planogram')}
            style={{
              flex: 1,
              padding: '0.8rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'planogram' ? 'var(--primary-color, #3b82f6)' : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Expected Products
          </button>
          <button
            onClick={() => setActiveTab('compliance_rules')}
            style={{
              flex: 1,
              padding: '0.8rem',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: activeTab === 'compliance_rules' ? 'var(--primary-color, #3b82f6)' : 'rgba(255,255,255,0.05)',
              color: '#fff',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Compliance Rules
          </button>
        </div>
      )}

      {/* Auth Views vs App Views */}
      {!token ? (
        authView === 'login' ? (
          <Login onSuccess={handleLoginSuccess} onSwitchToRegister={() => setAuthView('register')} />
        ) : (
          <Register onSuccess={handleLoginSuccess} onSwitchToLogin={() => setAuthView('login')} />
        )
      ) : activeTab === 'detection' && selectedImageForAnalysis ? (
        <ObjectDetectionView
          token={token}
          image={selectedImageForAnalysis}
          onBack={() => setActiveTab('images')}
        />
      ) : activeTab === 'ocr' && selectedImageForAnalysis ? (
        <OCRView
          token={token}
          image={selectedImageForAnalysis}
          onBack={() => setActiveTab('images')}
        />
      ) : activeTab === 'evidence' && selectedImageForAnalysis ? (
        <EvidenceView
          token={token}
          image={selectedImageForAnalysis}
          onBack={() => setActiveTab('images')}
        />
      ) : activeTab === 'expected_actual' && selectedImageForAnalysis ? (
        <ExpectedActualView
          token={token}
          image={selectedImageForAnalysis}
          onBack={() => setActiveTab('images')}
        />
      ) : activeTab === 'compliance' && selectedImageForAnalysis ? (
        <ComplianceView
          token={token}
          image={selectedImageForAnalysis}
          onBack={() => setActiveTab('images')}
        />
      ) : activeTab === 'compliance_rules' ? (
        <ComplianceRuleManager token={token} stores={stores} userRole={user.role} />
      ) : activeTab === 'planogram' ? (
        <ExpectedProductManager token={token} stores={stores} />
      ) : activeTab === 'images' ? (
        <ImageUpload
          token={token}
          stores={stores}
          onSelectImageForAnalysis={handleSelectImageForAnalysis}
          onSelectImageForOCR={handleSelectImageForOCR}
          onSelectImageForEvidence={handleSelectImageForEvidence}
          onSelectImageForExpectedActual={handleSelectImageForExpectedActual}
          onSelectImageForCompliance={handleSelectImageForCompliance}
        />
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
