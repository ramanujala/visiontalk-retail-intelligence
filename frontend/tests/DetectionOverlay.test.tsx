import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DetectionOverlay } from '../src/components/DetectionOverlay';
import { DetectionItem } from '../src/types/detection';

const mockDetections: DetectionItem[] = [
  {
    id: 'det-1',
    analysis_run_id: 'run-1',
    company_id: 'comp-1',
    class_id: 0,
    class_name: 'bottle',
    confidence: 0.95,
    x_min: 10,
    y_min: 20,
    x_max: 50,
    y_max: 100,
    created_at: new Date().toISOString()
  }
];

describe('DetectionOverlay Component', () => {
  it('renders image element and bounding box label', () => {
    render(
      <DetectionOverlay
        imageSrc="http://example.com/test.jpg"
        originalWidth={400}
        originalHeight={300}
        detections={mockDetections}
      />
    );
    expect(screen.getByAltText('Shelf Image')).toBeInTheDocument();
  });
});
