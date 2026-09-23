import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { EvidenceOverlay } from '../src/components/EvidenceOverlay';
import { CanonicalEvidenceResponse } from '../src/types/evidence';

const mockEvidence: CanonicalEvidenceResponse = {
  image_id: 'img-123',
  company_id: 'comp-123',
  evidence_version: '1.0',
  metadata: {
    image_id: 'img-123',
    company_id: 'comp-123',
    evidence_version: '1.0',
    total_detections: 1,
    total_ocr_regions: 1,
    total_associations: 1,
    generated_at: new Date().toISOString()
  },
  detections: [
    {
      id: 'det-1',
      analysis_run_id: 'run-1',
      class_id: 0,
      class_name: 'bottle',
      confidence: 0.95,
      bounding_box: { x_min: 10, y_min: 10, x_max: 100, y_max: 200 },
      related_ocr_ids: ['ocr-1'],
      spatial_relationships: [
        {
          ocr_id: 'ocr-1',
          ocr_text: '500ml',
          intersection_area: 500,
          iou: 0.45,
          ocr_overlap_ratio: 1.0,
          detection_overlap_ratio: 0.1,
          center_distance: 15.0,
          is_contained: true
        }
      ]
    }
  ],
  ocr_results: [
    {
      id: 'ocr-1',
      analysis_run_id: 'run-2',
      text: '500ml',
      normalized_text: '500ml',
      confidence: 0.98,
      line_order: 1,
      bounding_box: { x_min: 20, y_min: 150, x_max: 80, y_max: 180 }
    }
  ]
};

describe('EvidenceOverlay Component', () => {
  it('renders image element, detection boxes, and associated OCR badges', () => {
    render(
      <EvidenceOverlay
        imageSrc="http://example.com/shelf.jpg"
        evidence={mockEvidence}
      />
    );

    const imgEl = screen.getByAltText('Shelf Evidence');
    expect(imgEl).toBeInTheDocument();
    expect(imgEl).toHaveAttribute('src', 'http://example.com/shelf.jpg');

    expect(screen.getByText(/bottle \(95%\)/i)).toBeInTheDocument();
    expect(screen.getByText(/"500ml"/i)).toBeInTheDocument();
  });
});
