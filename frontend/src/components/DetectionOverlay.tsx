import React, { useRef, useState, useEffect } from 'react';
import { DetectionItem } from '../types/detection';

interface DetectionOverlayProps {
  imageSrc: string;
  originalWidth: number;
  originalHeight: number;
  detections: DetectionItem[];
  altText?: string;
}

export const DetectionOverlay: React.FC<DetectionOverlayProps> = ({
  imageSrc,
  originalWidth,
  originalHeight,
  detections,
  altText = 'Shelf Image'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [displayedSize, setDisplayedSize] = useState<{ width: number; height: number }>({ width: 0, height: 0 });

  const updateSize = () => {
    if (imgRef.current) {
      setDisplayedSize({
        width: imgRef.current.clientWidth,
        height: imgRef.current.clientHeight
      });
    }
  };

  useEffect(() => {
    window.addEventListener('resize', updateSize);
    return () => window.removeEventListener('resize', updateSize);
  }, []);

  // Compute scale factors
  const scaleX = originalWidth > 0 && displayedSize.width > 0 ? displayedSize.width / originalWidth : 1;
  const scaleY = originalHeight > 0 && displayedSize.height > 0 ? displayedSize.height / originalHeight : 1;

  // Distinct color palette for classes
  const getColor = (classId: number) => {
    const colors = ['#3b82f6', '#22c55e', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4', '#ef4444'];
    return colors[classId % colors.length];
  };

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        display: 'inline-block',
        maxWidth: '100%',
        borderRadius: '8px',
        overflow: 'hidden',
        border: '1px solid rgba(255,255,255,0.1)',
        backgroundColor: '#0f172a'
      }}
    >
      <img
        ref={imgRef}
        src={imageSrc}
        alt={altText}
        onLoad={updateSize}
        style={{
          display: 'block',
          maxWidth: '100%',
          height: 'auto'
        }}
      />

      {/* Render Resizable Bounding Box Overlay Badges */}
      {displayedSize.width > 0 &&
        detections.map((det) => {
          const left = det.x_min * scaleX;
          const top = det.y_min * scaleY;
          const width = (det.x_max - det.x_min) * scaleX;
          const height = (det.y_max - det.y_min) * scaleY;
          const color = getColor(det.class_id);

          return (
            <div
              key={det.id}
              style={{
                position: 'absolute',
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
                border: `2px solid ${color}`,
                backgroundColor: `${color}22`,
                pointerEvents: 'none',
                boxSizing: 'border-box',
                zIndex: 10
              }}
            >
              <span
                style={{
                  position: 'absolute',
                  top: '-20px',
                  left: '-2px',
                  backgroundColor: color,
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '1px 5px',
                  borderRadius: '3px 3px 3px 0',
                  whiteSpace: 'nowrap',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.5)'
                }}
              >
                {det.class_name} ({Math.round(det.confidence * 100)}%)
              </span>
            </div>
          );
        })}
    </div>
  );
};
