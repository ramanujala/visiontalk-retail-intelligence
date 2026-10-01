import React, { useEffect, useState } from 'react';
import { ImageItem } from '../types/image';
import { ComplianceAnalysisRunResponse, ComplianceSummaryResponse } from '../types/compliance';
import { executeComplianceAnalysis, fetchComplianceSummary } from '../services/compliance';
import styles from './Auth.module.css';

interface ComplianceViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const ComplianceView: React.FC<ComplianceViewProps> = ({ token, image, onBack }) => {
  const [summary, setSummary] = useState<ComplianceSummaryResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (force: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      await executeComplianceAnalysis(token, image.id, force);
      const sum = await fetchComplianceSummary(token, image.id);
      setSummary(sum);
    } catch (err: any) {
      setError(err.message || 'Failed to run compliance analysis.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAnalysis(false);
  }, [token, image.id]);

  return (
    <div className={styles.container} data-testid="compliance-view-page">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>
          &larr; Back to Gallery
        </button>
        <h2 className={styles.title}>Retail Compliance Evaluation (Phase 8)</h2>
        <button className={styles.reanalyzeButton} onClick={() => runAnalysis(true)} disabled={loading}>
          {loading ? 'Evaluating...' : 'Re-evaluate Rules'}
        </button>
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}

      {loading && !summary ? (
        <div className={styles.loadingState}>Evaluating Compliance Rules against Shelf Evidence...</div>
      ) : summary ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%' }}>
          {/* Summary Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)', textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: '#9ca3af' }}>Rules Evaluated</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#ffffff', marginTop: '4px' }}>{summary.total_rules}</div>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(34, 197, 94, 0.1)', borderRadius: '8px', border: '1px solid rgba(34, 197, 94, 0.2)', textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: '#4ade80' }}>Passed</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#4ade80', marginTop: '4px' }}>{summary.passed}</div>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', border: '1px solid rgba(239, 68, 68, 0.2)', textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: '#f87171' }}>Failed</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#f87171', marginTop: '4px' }}>{summary.failed}</div>
            </div>
            <div style={{ padding: '1rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.2)', textAlign: 'center' }}>
              <div style={{ fontSize: '0.8rem', color: '#fbbf24' }}>Critical / High</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#fbbf24', marginTop: '4px' }}>{summary.critical_findings + summary.high_findings}</div>
            </div>
          </div>

          {/* Detailed Findings List */}
          <div className={styles.detectionsCard}>
            <h3 style={{ marginBottom: '1rem' }}>Compliance Findings</h3>
            {summary.findings.length === 0 ? (
              <p className={styles.emptyText}>No active compliance rules evaluated for this image.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                {summary.findings.map((f) => (
                  <div
                    key={f.id}
                    style={{
                      padding: '1rem',
                      borderRadius: '6px',
                      backgroundColor: 'rgba(255,255,255,0.03)',
                      borderLeft: `4px solid ${f.status === 'PASS' ? '#22c55e' : f.severity === 'CRITICAL' || f.severity === 'HIGH' ? '#ef4444' : '#f59e0b'}`,
                      borderTop: '1px solid rgba(255,255,255,0.05)',
                      borderRight: '1px solid rgba(255,255,255,0.05)',
                      borderBottom: '1px solid rgba(255,255,255,0.05)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.9rem', color: f.status === 'PASS' ? '#4ade80' : '#f87171' }}>
                        [{f.status}] &bull; SEVERITY: {f.severity}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        Evidence Refs: {f.evidence_references.length}
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.95rem', color: '#e2e8f0', fontWeight: 500 }}>{f.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};
