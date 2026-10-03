import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ConversationView } from '../src/pages/ConversationView';

describe('ConversationView Component', () => {
  it('renders conversation view title and sidebar elements', () => {
    render(<ConversationView token="mock-token" />);

    expect(screen.getByText(/Audit Chat Sessions/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/New Chat Title\.\.\./i)).toBeInTheDocument();
    expect(screen.getByText(/\+ New/i)).toBeInTheDocument();
  });
});
