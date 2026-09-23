import React, { useEffect, useState } from 'react';
import { ImageItem } from '../types/image';
import { CanonicalEvidenceResponse, EvidenceDetectionItem } from '../types/evidence';
import { fetchCanonicalEvidence } from '../services/evidence';
import { EvidenceOverlay } from '../components/EvidenceOverlay';
import styles from './ObjectDetectionView.module.css';

interface EvidenceViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const EvidenceView: React.FC<EvidenceViewProps> = ({ token, image, onBack }) => {
  const [evidence, setEvidence] = useState<CanonicalEvidenceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDetection, setSelectedDetection] = useState<EvidenceDetectionItem | null>(null);

  const loadEvidence = async (forceRegenerate: boolean = false) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchCanonicalEvidence(token, image.id, forceRegenerate);
      setEvidence(data);
      if (data.detections.length > 0) {
        setSelectedDetection(data.detections[0]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load evidence');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEvidence(false);
  }, [token, image.id]);

  const imageUrl = `http://localhost:8000/api/v1/images/${image.id}/file`;

  return (
    <div className={styles.container} data-testid="evidence-view-page">
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>
          &larr; Back to Gallery
        </button>
        <h2 className={styles.title}>Canonical Evidence Layer (Phase 6)</h2>
        <button className={styles.reanalyzeButton} onClick={() => loadEvidence(true)} disabled={loading}>
          {loading ? 'Processing...' : 'Regenerate Evidence'}
        </button>
      </div>

      {error && <div className={styles.errorMessage}>{error}</div>}

      {loading && !evidence ? (
        <div className={styles.loadingState}>Aggregating Canonical Evidence from Detections & OCR...</div>
      ) : evidence ? (
        <div className={styles.contentGrid}>
          {/* Visual Canvas Panel */}
          <div className={styles.imagePanel}>
            <EvidenceOverlay imageSrc={imageUrl} evidence={evidence} />
          </div>

          {/* Structured Evidence Panel */}
          <div className={styles.sidebar}>
            <div className={styles.summaryCard}>
              <h3>Evidence Summary</h3>
              <p>
                <strong>Version:</strong> {evidence.evidence_version}
              </p>
              <p>
                <strong>Total Detections:</strong> {evidence.metadata.total_detections}
              </p>
              <p>
                <strong>Total OCR Text Regions:</strong> {evidence.metadata.total_ocr_regions}
              </p>
              <p>
                <strong>Spatial Associations:</strong> {evidence.metadata.total_associations}
              </p>
            </div>

            {/* Detections & Spatial Associations List */}
            <div className={styles.detectionsCard}>
              <h3>Detected Objects & Spatial Associations</h3>
              {evidence.detections.length === 0 ? (
                <p className={styles.emptyText}>No object detections recorded for this image.</p>
              ) : (
                <div className={styles.detectionList}>
                  {evidence.detections.map((det) => {
                    const isSelected = selectedDetection?.id === det.id;
                    return (
                      <div
                        key={det.id}
                        className={`${styles.detectionItem} ${isSelected ? styles.selectedItem : ''}`}
                        onClick={() => setSelectedDetection(det)}
                        style={{ padding: '0.75rem', marginBottom: '0.5rem', borderRadius: '6px', backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255,255,255,0.03)', border: isSelected ? '1px solid #3b82f6' : '1px solid rgba(255,255,255,0.08)' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                          <span>{det.class_name}</span>
                          <span style={{ color: '#10b981' }}>{(det.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '4px' }}>
                          Bounding Box: [{det.bounding_box.x_min}, {det.bounding_box.y_min}, {det.bounding_box.x_max}, {det.bounding_box.y_max}]
                        </div>
                        {det.spatial_relationships.length > 0 && (
                          <div style={{ marginTop: '6px', fontSize: '0.82rem', backgroundColor: 'rgba(245, 158, 11, 0.1)', padding: '6px', borderRadius: '4px', borderLeft: '3px solid #f59e0b' }}>
                            <strong>Associated OCR:</strong>
                            {det.spatial_relationships.map((rel, idx) => (
                              <div key={idx} style={{ marginTop: '2px' }}>
                                &bull; "{rel.ocr_text}" (IoU: {rel.iou}, Overlap: {(rel.ocr_overlap_ratio * 100).toFixed(0)}%)
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* OCR Observations Panel */}
            <div className={styles.detectionsCard} style={{ marginTop: '1rem' }}>
              <h3>OCR Text Observations</h3>
              {evidence.ocr_results.length === 0 ? (
                <p className={styles.emptyText}>No text extracted for this image.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {evidence.ocr_results.map((ocr) => (
                    <div key={ocr.id} style={{ padding: '0.5rem', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.05)', fontSize: '0.85rem' }}>
                      <span style={{ fontWeight: 600, color: '#f59e0b' }}>Line {ocr.line_order}: </span>
                      <span>"{ocr.normalized_text}"</span>
                      <span style={{ float: 'right', color: '#9ca3af' }}>{(ocr.confidence * 100).toFixed(0)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
