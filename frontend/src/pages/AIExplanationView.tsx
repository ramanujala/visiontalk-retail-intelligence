import React, { useEffect, useState } from 'react';
import { ImageItem } from '../types/image';
import { LLMExplanationResponse } from '../types/llm';
import { fetchImageExplanation } from '../services/llm';
import styles from './Auth.module.css';

interface AIExplanationViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const AIExplanationView: React.FC<AIExplanationViewProps> = ({ token, image, onBack }) => {
  const [data, setData] = useState<LLMExplanationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [focusInquiry, setFocusInquiry] = useState<string>('');

  const loadExplanation = async (force: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchImageExplanation(token, image.id, force, focusInquiry || undefined);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to generate AI explanation.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExplanation(false);
  }, [token, image.id]);

  return (
    <div className={styles.container} data-testid="ai-explanation-view-page">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>
          ← Back to Gallery
        </button>
        <h2 className={styles.title}>AI Grounded Explanation (Phase 9 — Gemini LLM)</h2>
        <button
          className={styles.reanalyzeButton}
          onClick={() => loadExplanation(true)}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Re-generate Explanation'}
        </button>
      </div>

      <div style={{ marginBottom: '1.5rem', backgroundColor: 'rgba(255,255,255,0.03)', padding: '1rem', borderRadius: '8px' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Focus Audit Inquiry (Optional)</h4>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            className={styles.input}
            placeholder="e.g. Focus on beverage section pricing and stock levels..."
            value={focusInquiry}
            onChange={(e) => setFocusInquiry(e.target.value)}
          />
          <button
            onClick={() => loadExplanation(true)}
            className={styles.submitBtn}
            style={{ marginTop: 0, whiteSpace: 'nowrap' }}
            disabled={loading}
          >
            Ask Gemini
          </button>
        </div>
      </div>

      {loading ? (
        <div className={styles.loadingState}>
          Synthesizing grounded natural language explanation from verified shelf evidence...
        </div>
      ) : error ? (
        <div className={styles.errorMessage}>{error}</div>
      ) : data ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Status & Confidence Banner */}
          <div style={{
            display: 'flex',
            justify: 'space-between',
            alignItems: 'center',
            backgroundColor: data.status === 'EXPLAINED' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(245, 158, 11, 0.1)',
            border: `1px solid ${data.status === 'EXPLAINED' ? '#22c55e' : '#f59e0b'}`,
            padding: '1rem',
            borderRadius: '8px'
          }}>
            <div>
              <span style={{
                fontWeight: 700,
                fontSize: '0.9rem',
                color: data.status === 'EXPLAINED' ? '#4ade80' : '#fbbf24',
                textTransform: 'uppercase'
              }}>
                STATUS: {data.status} {data.fallback_reason ? `(${data.fallback_reason})` : ''}
              </span>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                Model: <strong>{data.model}</strong> | Generated: {new Date(data.created_at).toLocaleString()}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Evidence Confidence</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#3b82f6' }}>
                {(data.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Key Findings Card */}
          <div className={styles.authCard} style={{ maxWidth: '100%', margin: 0 }}>
            <h3 className={styles.authTitle} style={{ fontSize: '1.1rem', textAlign: 'left', marginBottom: '0.8rem' }}>
              Key Operational Findings
            </h3>
            <ul style={{ margin: 0, paddingLeft: '1.2rem', color: 'var(--text-primary)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {data.key_findings.map((finding, idx) => (
                <li key={idx} style={{ fontSize: '0.95rem' }}>{finding}</li>
              ))}
            </ul>
          </div>

          {/* Natural Language Explanation Card */}
          <div className={styles.authCard} style={{ maxWidth: '100%', margin: 0 }}>
            <h3 className={styles.authTitle} style={{ fontSize: '1.1rem', textAlign: 'left', marginBottom: '0.8rem' }}>
              Grounded AI Narrative
            </h3>
            <div style={{
              whiteSpace: 'pre-wrap',
              fontSize: '0.95rem',
              lineHeight: '1.6',
              color: 'var(--text-primary)',
              backgroundColor: 'rgba(0,0,0,0.2)',
              padding: '1rem',
              borderRadius: '6px',
              fontFamily: 'sans-serif'
            }}>
              {data.explanation}
            </div>
          </div>

          {/* Traceable Evidence References */}
          <div className={styles.authCard} style={{ maxWidth: '100%', margin: 0 }}>
            <h3 className={styles.authTitle} style={{ fontSize: '1.1rem', textAlign: 'left', marginBottom: '0.8rem' }}>
              Verified Evidence Traceability
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.8rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Detections Verified</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{data.evidence_references.detection_count || 0} items</div>
              </div>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.8rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>OCR Snippets Verified</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{data.evidence_references.ocr_count || 0} texts</div>
              </div>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.8rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Compliance Checks</div>
                <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>{data.evidence_references.compliance_findings_count || 0} findings</div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
