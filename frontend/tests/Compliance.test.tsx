import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ComplianceRuleManager } from '../src/components/ComplianceRuleManager';
import { ComplianceView } from '../src/pages/ComplianceView';

const mockStores = [
  { id: 'store-1', company_id: 'comp-1', name: 'Store Alpha', code: 'SA1', is_active: true, created_at: '', updated_at: '' }
];

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

describe('Compliance UI Components', () => {
  it('renders ComplianceRuleManager correctly', () => {
    render(<ComplianceRuleManager token="mock-token" stores={mockStores} userRole="ADMIN" />);

    expect(screen.getByText(/Configure Retail Compliance Rules/i)).toBeInTheDocument();
    expect(screen.getByText(/Add Rule/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Rule Type/i)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Severity/i)[0]).toBeInTheDocument();
  });

  it('renders ComplianceView controls correctly', () => {
    render(<ComplianceView token="mock-token" image={mockImage} onBack={() => {}} />);

    expect(screen.getByText(/Retail Compliance Evaluation \(Phase 8\)/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Evaluating/i)[0]).toBeInTheDocument();
  });
});
