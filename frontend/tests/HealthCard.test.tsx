import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { HealthCard } from '../src/components/HealthCard';

describe('HealthCard Component', () => {
  it('renders health check title and healthy status', () => {
    const handleRefresh = vi.fn();
    render(
      <HealthCard
        liveness={{ status: 'healthy', version: '1.0.0', timestamp: '2026-08-20T10:00:00Z' }}
        readiness={{ status: 'ready', database_connected: true, version: '1.0.0', timestamp: '2026-08-20T10:00:00Z' }}
        loading={false}
        error={null}
        onRefresh={handleRefresh}
      />
    );

    expect(screen.getByTestId('health-card')).toBeInTheDocument();
    expect(screen.getByText('System Status & Health Check')).toBeInTheDocument();
    expect(screen.getByText('healthy')).toBeInTheDocument();
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('renders disconnected state when error is provided', () => {
    const handleRefresh = vi.fn();
    render(
      <HealthCard
        liveness={null}
        readiness={null}
        loading={false}
        error="Backend connection failed"
        onRefresh={handleRefresh}
      />
    );

    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });
});
