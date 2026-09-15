import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ImageUpload } from '../src/pages/ImageUpload';
import { Store } from '../src/types/store';

const mockStores: Store[] = [
  { id: 'store-1', company_id: 'comp-1', name: 'Downtown Store', code: 'STR-001', is_active: true }
];

describe('ImageUpload Component', () => {
  it('renders store select and image file input', () => {
    render(<ImageUpload token="mock-token" stores={mockStores} />);
    expect(screen.getByText(/Upload Retail Shelf Image/i)).toBeInTheDocument();
    expect(screen.getByText(/Select Target Store/i)).toBeInTheDocument();
    expect(screen.getByText(/Choose Image/i)).toBeInTheDocument();
  });
});
