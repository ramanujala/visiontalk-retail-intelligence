import React, { useEffect, useState } from 'react';
import { ImageItem } from '../types/image';
import { ExpectedActualAnalysisRunResponse, ExpectedActualItem, ExpectedActualIssue } from '../types/expected_actual';
import { runExpectedVsActualAnalysis } from '../services/expected_actual';
import styles from './ObjectDetectionView.module.css';

interface ExpectedActualViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const ExpectedActualView: React.FC<ExpectedActualViewProps> = ({ token, image, onBack }) => {
  const [analysis, setAnalysis] = useState<ExpectedActualAnalysisRunResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const executeAnalysis = async (force: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = await runExpectedVsActualAnalysis(token, image.id, force);
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || 'Failed to run Expected vs Actual analysis');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeAnalysis(false);
  }, [token, image.id]);

  const getStatusBadgeStyle = (status: string) => {
    switch (status) {
      case 'OBSERVED':
        return { backgroundColor: 'rgba(34, 197, 94, 0.2)', color: '#4ade80' };
      case 'MISSING':
        return { backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#f87171' };
      case 'LOW_STOCK':
        return { backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fbbf24' };
      case 'EXCESS':
        return { backgroundColor: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' };
      case 'UNEXPECTED':
      case 'UNMATCHED':
        return { backgroundColor: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' };
      default:
        return { backgroundColor: 'rgba(255, 255, 255, 0.1)', color: '#ffffff' };
    }
  };

  return (
    <div className={styles.container} data-testid="expected-actual-view-page">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>
          &larr; Back to Gallery
        </button>
        <h2 className={styles.title}>Expected vs Actual Retail Analysis (Phase 7)</h2>
        <button className={styles.reanalyzeButton} onClick={() => executeAnalysis(true)} disabled={loading}>
          {loading ? 'Analyzing...' : 'Re-run Comparison'}
        </button>
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}

      {loading && !analysis ? (
        <div className={styles.loadingState}>Comparing Store Expectations against Canonical Evidence...</div>
      ) : analysis ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%' }}>
          {/* Comparison Table */}
          <div className={styles.summaryCard} style={{ overflowX: 'auto' }}>
            <h3 style={{ marginBottom: '1rem' }}>Shelf Inventory Comparison Table</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.9rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#9ca3af' }}>
                  <th style={{ padding: '0.6rem' }}>Product Code</th>
                  <th style={{ padding: '0.6rem' }}>Product Name</th>
                  <th style={{ padding: '0.6rem' }}>Expected Qty</th>
                  <th style={{ padding: '0.6rem' }}>Observed Qty</th>
                  <th style={{ padding: '0.6rem' }}>Difference</th>
                  <th style={{ padding: '0.6rem' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {analysis.expected_actual_items.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ padding: '1rem', textAlign: 'center', color: '#9ca3af' }}>
                      No comparison items recorded.
                    </td>
                  </tr>
                ) : (
                  analysis.expected_actual_items.map((item) => (
                    <tr key={item.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.6rem', fontWeight: 600 }}>{item.product_code}</td>
                      <td style={{ padding: '0.6rem' }}>{item.product_name}</td>
                      <td style={{ padding: '0.6rem' }}>{item.expected_quantity}</td>
                      <td style={{ padding: '0.6rem' }}>{item.observed_quantity}</td>
                      <td style={{ padding: '0.6rem', fontWeight: 600, color: item.difference < 0 ? '#f87171' : item.difference > 0 ? '#60a5fa' : '#4ade80' }}>
                        {item.difference > 0 ? `+${item.difference}` : item.difference}
                      </td>
                      <td style={{ padding: '0.6rem' }}>
                        <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, ...getStatusBadgeStyle(item.status) }}>
                          {item.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Structured Issues List */}
          <div className={styles.detectionsCard}>
            <h3 style={{ marginBottom: '1rem' }}>Discrepancies & Structured Issues ({analysis.expected_actual_issues.length})</h3>
            {analysis.expected_actual_issues.length === 0 ? (
              <p className={styles.emptyText}>All expected products match observed evidence perfectly! No issues flagged.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {analysis.expected_actual_issues.map((issue) => (
                  <div
                    key={issue.id}
                    style={{
                      padding: '0.8rem 1rem',
                      borderRadius: '6px',
                      backgroundColor: 'rgba(255,255,255,0.03)',
                      borderLeft: `4px solid ${issue.severity === 'HIGH' ? '#ef4444' : issue.severity === 'MEDIUM' ? '#f59e0b' : '#3b82f6'}`,
                      borderTop: '1px solid rgba(255,255,255,0.05)',
                      borderRight: '1px solid rgba(255,255,255,0.05)',
                      borderBottom: '1px solid rgba(255,255,255,0.05)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem', color: issue.severity === 'HIGH' ? '#f87171' : issue.severity === 'MEDIUM' ? '#fbbf24' : '#60a5fa' }}>
                        [{issue.issue_type}] &bull; SEVERITY: {issue.severity}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        Evidence Refs: {issue.evidence_references.length}
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: '0.9rem', color: '#e2e8f0' }}>{issue.message}</p>
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
