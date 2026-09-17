import React, { useState } from 'react';
import { ImageItem } from '../types/image';
import { AnalysisRun } from '../types/detection';
import { analyzeImage } from '../services/detections';
import { DetectionOverlay } from '../components/DetectionOverlay';
import styles from '../pages/Auth.module.css';

interface ObjectDetectionViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const ObjectDetectionView: React.FC<ObjectDetectionViewProps> = ({ token, image, onBack }) => {
  const [analysisRun, setAnalysisRun] = useState<AnalysisRun | null>(null);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunAnalysis = async (forceReanalyze: boolean = false) => {
    setAnalyzing(true);
    setError(null);
    try {
      const result = await analyzeImage(token, image.id, forceReanalyze);
      setAnalysisRun(result);
    } catch (err: any) {
      setError(err.message || 'Detection analysis failed.');
    } finally {
      setAnalyzing(false);
    }
  };

  // Construct image display URL
  const imageUrl = `/storage_uploads/${image.storage_key}`;

  return (
    <div className={styles.storesContainer} style={{ marginTop: '2rem' }}>
      <div className={styles.authCard} style={{ maxWidth: '100%', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <div>
            <button
              onClick={onBack}
              style={{
                backgroundColor: 'transparent',
                border: '1px solid rgba(255,255,255,0.2)',
                color: 'var(--text-secondary)',
                padding: '0.3rem 0.8rem',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                marginBottom: '0.5rem'
              }}
            >
              ← Back to Image Gallery
            </button>
            <h3 className={styles.authTitle} style={{ fontSize: '1.3rem', textAlign: 'left', margin: 0 }}>
              YOLO Object Detection & Bounding Box Perception
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0 0' }}>
              Target Image: <strong>{image.original_filename}</strong> ({image.width}x{image.height} px)
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.8rem' }}>
            <button
              onClick={() => handleRunAnalysis(false)}
              className={styles.submitBtn}
              style={{ marginTop: 0 }}
              disabled={analyzing}
            >
              {analyzing ? 'Running Detection...' : analysisRun ? 'Re-fetch Analysis' : 'Run Detection'}
            </button>
            {analysisRun && (
              <button
                onClick={() => handleRunAnalysis(true)}
                style={{
                  backgroundColor: 'transparent',
                  border: '1px solid var(--primary-color, #3b82f6)',
                  color: 'var(--primary-color, #3b82f6)',
                  padding: '0.6rem 1rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}
                disabled={analyzing}
              >
                Force Re-Analysis
              </button>
            )}
          </div>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        {/* Visualizer & Inspection Pane */}
        <div style={{ display: 'grid', gridTemplateColumns: analysisRun ? '1fr 320px' : '1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
          <div style={{ textAlign: 'center' }}>
            <DetectionOverlay
              imageSrc={imageUrl}
              originalWidth={image.width}
              originalHeight={image.height}
              detections={analysisRun ? analysisRun.detections : []}
              altText={image.original_filename}
            />
          </div>

          {analysisRun && (
            <div style={{ backgroundColor: 'rgba(255,255,255,0.03)', padding: '1.2rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)', textAlign: 'left' }}>
              <h4 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1.05rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem' }}>
                Perception Evidence Summary
              </h4>

              <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Status: </span>
                  <strong style={{ color: analysisRun.status === 'COMPLETED' ? '#4ade80' : '#f87171' }}>{analysisRun.status}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Model Engine: </span>
                  <strong>{analysisRun.model_name} ({analysisRun.model_version})</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Total Detections: </span>
                  <strong style={{ fontSize: '1.1rem', color: '#3b82f6' }}>{analysisRun.detections.length}</strong>
                </div>
              </div>

              <h5 style={{ margin: '1.2rem 0 0.6rem 0', color: '#fff', fontSize: '0.95rem' }}>
                Detected Objects Breakdown:
              </h5>

              {analysisRun.detections.length === 0 ? (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No objects detected above confidence threshold ({0.25}).</p>
              ) : (
                <div style={{ maxHeight: '250px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {analysisRun.detections.map((d, i) => (
                    <div key={d.id || i} style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.5rem 0.8rem', borderRadius: '4px', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, color: '#fff' }}>{d.class_name}</span>
                      <span style={{ color: '#4ade80', fontWeight: 600 }}>{Math.round(d.confidence * 100)}%</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
