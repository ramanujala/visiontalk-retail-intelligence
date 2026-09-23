import React, { useState } from 'react';
import { ImageItem } from '../types/image';
import { OCRAnalysisRun } from '../types/ocr';
import { analyzeImageText } from '../services/ocr';
import { OCROverlay } from '../components/OCROverlay';
import styles from '../pages/Auth.module.css';

interface OCRViewProps {
  token: string;
  image: ImageItem;
  onBack: () => void;
}

export const OCRView: React.FC<OCRViewProps> = ({ token, image, onBack }) => {
  const [ocrRun, setOcrRun] = useState<OCRAnalysisRun | null>(null);
  const [extracting, setExtracting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleRunOCR = async (forceReanalyze: boolean = false) => {
    setExtracting(true);
    setError(null);
    try {
      const result = await analyzeImageText(token, image.id, forceReanalyze);
      setOcrRun(result);
    } catch (err: any) {
      setError(err.message || 'OCR text extraction failed.');
    } finally {
      setExtracting(false);
    }
  };

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
              PaddleOCR Text Extraction & Recognition
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0 0' }}>
              Target Image: <strong>{image.original_filename}</strong> ({image.width}x{image.height} px)
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.8rem' }}>
            <button
              onClick={() => handleRunOCR(false)}
              className={styles.submitBtn}
              style={{ marginTop: 0 }}
              disabled={extracting}
            >
              {extracting ? 'Extracting Text...' : ocrRun ? 'Re-fetch OCR' : 'Extract Text (OCR)'}
            </button>
            {ocrRun && (
              <button
                onClick={() => handleRunOCR(true)}
                style={{
                  backgroundColor: 'transparent',
                  border: '1px solid #a855f7',
                  color: '#a855f7',
                  padding: '0.6rem 1rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontWeight: 600,
                  fontSize: '0.9rem'
                }}
                disabled={extracting}
              >
                Force Re-Analysis
              </button>
            )}
          </div>
        </div>

        {error && <div className={styles.errorMessage}>{error}</div>}

        {/* Visualizer & Inspection Pane */}
        <div style={{ display: 'grid', gridTemplateColumns: ocrRun ? '1fr 340px' : '1fr', gap: '1.5rem', marginTop: '1.5rem' }}>
          <div style={{ textAlign: 'center' }}>
            <OCROverlay
              imageSrc={imageUrl}
              originalWidth={image.width}
              originalHeight={image.height}
              ocrResults={ocrRun ? ocrRun.ocr_results : []}
              altText={image.original_filename}
            />
          </div>

          {ocrRun && (
            <div style={{ backgroundColor: 'rgba(255,255,255,0.03)', padding: '1.2rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)', textAlign: 'left' }}>
              <h4 style={{ margin: '0 0 1rem 0', color: '#fff', fontSize: '1.05rem', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '0.5rem' }}>
                OCR Text Evidence Summary
              </h4>

              <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Status: </span>
                  <strong style={{ color: ocrRun.status === 'COMPLETED' ? '#4ade80' : '#f87171' }}>{ocrRun.status}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>OCR Engine: </span>
                  <strong>{ocrRun.model_name} ({ocrRun.model_version})</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--text-secondary)' }}>Text Regions Found: </span>
                  <strong style={{ fontSize: '1.1rem', color: '#a855f7' }}>{ocrRun.ocr_results.length}</strong>
                </div>
              </div>

              <h5 style={{ margin: '1.2rem 0 0.6rem 0', color: '#fff', fontSize: '0.95rem' }}>
                Recognized Text Items:
              </h5>

              {ocrRun.ocr_results.length === 0 ? (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No text regions detected above confidence threshold ({0.50}).</p>
              ) : (
                <div style={{ maxHeight: '280px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                  {ocrRun.ocr_results.map((r) => (
                    <div key={r.id} style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '0.6rem 0.8rem', borderRadius: '4px', fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: '#fff' }}>{r.normalized_text}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Line #{r.line_order}</div>
                      </div>
                      <span style={{ color: '#4ade80', fontWeight: 600 }}>{Math.round(r.confidence * 100)}%</span>
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
