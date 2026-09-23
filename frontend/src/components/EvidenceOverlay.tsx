import React, { useState } from 'react';
import { CanonicalEvidenceResponse, EvidenceDetectionItem, EvidenceOCRItem } from '../types/evidence';

interface EvidenceOverlayProps {
  imageSrc: string;
  evidence: CanonicalEvidenceResponse;
}

export const EvidenceOverlay: React.FC<EvidenceOverlayProps> = ({ imageSrc, evidence }) => {
  const [hoveredDetId, setHoveredDetId] = useState<string | null>(null);

  const activeDet = evidence.detections.find((d) => d.id === hoveredDetId);
  const activeOcrIds = activeDet ? activeDet.related_ocr_ids : [];

  return (
    <div style={{ position: 'relative', display: 'inline-block', maxWidth: '100%' }} data-testid="evidence-overlay-container">
      <img src={imageSrc} alt="Shelf Evidence" style={{ display: 'block', maxWidth: '100%', height: 'auto' }} />

      {/* Render Object Detections */}
      {evidence.detections.map((det) => {
        const isHovered = det.id === hoveredDetId;
        return (
          <div
            key={det.id}
            data-testid={`evidence-det-box-${det.id}`}
            onMouseEnter={() => setHoveredDetId(det.id)}
            onMouseLeave={() => setHoveredDetId(null)}
            style={{
              position: 'absolute',
              left: `${det.bounding_box.x_min}px`,
              top: `${det.bounding_box.y_min}px`,
              width: `${det.bounding_box.x_max - det.bounding_box.x_min}px`,
              height: `${det.bounding_box.y_max - det.bounding_box.y_min}px`,
              border: isHovered ? '3px solid #3b82f6' : '2px solid #10b981',
              backgroundColor: isHovered ? 'rgba(59, 130, 246, 0.2)' : 'rgba(16, 185, 129, 0.1)',
              boxSizing: 'border-box',
              cursor: 'pointer',
              zIndex: isHovered ? 20 : 10
            }}
          >
            <span
              style={{
                position: 'absolute',
                top: '-24px',
                left: '0px',
                backgroundColor: isHovered ? '#3b82f6' : '#10b981',
                color: '#ffffff',
                padding: '2px 6px',
                fontSize: '11px',
                fontWeight: 600,
                borderRadius: '4px',
                whiteSpace: 'nowrap'
              }}
            >
              {det.class_name} ({(det.confidence * 100).toFixed(0)}%)
            </span>
          </div>
        );
      })}

      {/* Render OCR Regions */}
      {evidence.ocr_results.map((ocr) => {
        const isAssociated = activeOcrIds.includes(ocr.id);
        return (
          <div
            key={ocr.id}
            data-testid={`evidence-ocr-box-${ocr.id}`}
            style={{
              position: 'absolute',
              left: `${ocr.bounding_box.x_min}px`,
              top: `${ocr.bounding_box.y_min}px`,
              width: `${ocr.bounding_box.x_max - ocr.bounding_box.x_min}px`,
              height: `${ocr.bounding_box.y_max - ocr.bounding_box.y_min}px`,
              border: isAssociated ? '2px dashed #f59e0b' : '1px solid rgba(245, 158, 11, 0.6)',
              backgroundColor: isAssociated ? 'rgba(245, 158, 11, 0.3)' : 'rgba(245, 158, 11, 0.08)',
              boxSizing: 'border-box',
              pointerEvents: 'none',
              zIndex: isAssociated ? 15 : 5
            }}
          >
            <span
              style={{
                position: 'absolute',
                bottom: '-20px',
                left: '0px',
                backgroundColor: isAssociated ? '#f59e0b' : 'rgba(0,0,0,0.7)',
                color: '#ffffff',
                padding: '1px 4px',
                fontSize: '10px',
                borderRadius: '3px',
                whiteSpace: 'nowrap'
              }}
            >
              "{ocr.normalized_text}"
            </span>
          </div>
        );
      })}
    </div>
  );
};
