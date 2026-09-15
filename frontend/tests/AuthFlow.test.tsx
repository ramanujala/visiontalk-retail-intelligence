import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Login } from '../src/pages/Login';
import { Register } from '../src/pages/Register';

describe('Frontend Authentication UI Components', () => {
  it('renders Login form correctly', () => {
    const handleSuccess = vi.fn();
    const handleSwitch = vi.fn();

    render(<Login onSuccess={handleSuccess} onSwitchToRegister={handleSwitch} />);

    expect(screen.getByText('Sign In to VisionTalk')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('admin@company.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  it('switches from Login to Register form on link click', () => {
    const handleSuccess = vi.fn();
    const handleSwitch = vi.fn();

    render(<Login onSuccess={handleSuccess} onSwitchToRegister={handleSwitch} />);

    const registerLink = screen.getByText('Register Company');
    fireEvent.click(registerLink);

    expect(handleSwitch).toHaveBeenCalledTimes(1);
  });

  it('renders Register Company form correctly', () => {
    const handleSuccess = vi.fn();
    const handleSwitch = vi.fn();

    render(<Register onSuccess={handleSuccess} onSwitchToLogin={handleSwitch} />);

    expect(screen.getByText('Register Company Workspace')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Vision Retail Solutions')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('vision-retail')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Register Company' })).toBeInTheDocument();
  });
});
