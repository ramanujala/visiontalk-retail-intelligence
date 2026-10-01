import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { AIExplanationView } from '../src/pages/AIExplanationView';

const mockImage = {
  id: 'img-1',
  company_id: 'comp-1',
  store_id: 'store-1',
  original_filename: 'shelf.jpg',
  storage_path: '/uploads/shelf.jpg',
  file_size: 102400,
  mime_type: 'image/jpeg',
  width: 1920,
  height: 1080,
  quality_score: 90,
  quality_flags: [],
  created_at: '',
  updated_at: ''
};

describe('AIExplanationView Component', () => {
  it('renders title and loading state controls', () => {
    render(<AIExplanationView token="mock-token" image={mockImage} onBack={() => {}} />);

    expect(screen.getByText(/AI Grounded Explanation \(Phase 9 — Gemini LLM\)/i)).toBeInTheDocument();
    expect(screen.getByText(/Ask Gemini/i)).toBeInTheDocument();
  });
});
