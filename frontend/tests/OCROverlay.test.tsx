import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { OCROverlay } from '../src/components/OCROverlay';
import { OCRResultItem } from '../src/types/ocr';

const mockOCRResults: OCRResultItem[] = [
  {
    id: 'ocr-1',
    analysis_run_id: 'run-1',
    company_id: 'comp-1',
    text: '  $9.99  ',
    normalized_text: '$9.99',
    confidence: 0.95,
    line_order: 1,
    x_min: 10,
    y_min: 20,
    x_max: 50,
    y_max: 100,
    created_at: new Date().toISOString()
  }
];

describe('OCROverlay Component', () => {
  it('renders image element and OCR text badge', () => {
    render(
      <OCROverlay
        imageSrc="http://example.com/test.jpg"
        originalWidth={400}
        originalHeight={300}
        ocrResults={mockOCRResults}
      />
    );
    expect(screen.getByAltText('Shelf Image')).toBeInTheDocument();
  });
});
