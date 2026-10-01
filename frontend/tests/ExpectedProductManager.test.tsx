import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ExpectedProductManager } from '../src/components/ExpectedProductManager';

const mockStores = [
  { id: 'store-1', company_id: 'comp-1', name: 'Store Alpha', code: 'SA1', is_active: true, created_at: '', updated_at: '' }
];

describe('ExpectedProductManager Component', () => {
  it('renders store select and expectation form inputs', () => {
    render(<ExpectedProductManager token="mock-token" stores={mockStores} />);

    expect(screen.getByText(/Configure Expected Products Planogram/i)).toBeInTheDocument();
    expect(screen.getByText(/Select Store/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g. Organic Milk/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g. BOTTLE/i)).toBeInTheDocument();
  });
});
