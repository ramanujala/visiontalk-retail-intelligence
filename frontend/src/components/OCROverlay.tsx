import React, { useRef, useState, useEffect } from 'react';
import { OCRResultItem } from '../types/ocr';

interface OCROverlayProps {
  imageSrc: string;
  originalWidth: number;
  originalHeight: number;
  ocrResults: OCRResultItem[];
  altText?: string;
}

export const OCROverlay: React.FC<OCROverlayProps> = ({
  imageSrc,
  originalWidth,
  originalHeight,
  ocrResults,
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

      {/* Render Resizable Text Bounding Box Overlay Badges */}
      {displayedSize.width > 0 &&
        ocrResults.map((res) => {
          const left = res.x_min * scaleX;
          const top = res.y_min * scaleY;
          const width = (res.x_max - res.x_min) * scaleX;
          const height = (res.y_max - res.y_min) * scaleY;

          return (
            <div
              key={res.id}
              style={{
                position: 'absolute',
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
                border: '2px solid #a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.2)',
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
                  backgroundColor: '#9333ea',
                  color: '#ffffff',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '1px 5px',
                  borderRadius: '3px 3px 3px 0',
                  whiteSpace: 'nowrap',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.5)'
                }}
              >
                {res.normalized_text} ({Math.round(res.confidence * 100)}%)
              </span>
            </div>
          );
        })}
    </div>
  );
};
