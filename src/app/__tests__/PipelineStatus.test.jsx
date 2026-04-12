import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PipelineStatus from '../components/PipelineStatus';

describe('PipelineStatus', () => {
  it('renders all three pipeline stages', () => {
    render(
      <PipelineStatus stage1="active" stage2="idle" connectionStatus="connected" />
    );
    expect(screen.getByText('Connection')).toBeInTheDocument();
    expect(screen.getByText('Stage 1')).toBeInTheDocument();
    expect(screen.getByText('Stage 2')).toBeInTheDocument();
  });

  it('handles null status values without crashing', () => {
    expect(() => {
      render(
        <PipelineStatus stage1={null} stage2={undefined} connectionStatus={null} />
      );
    }).not.toThrow();
  });

  it('shows correct labels for known statuses', () => {
    render(
      <PipelineStatus stage1="active" stage2="idle" connectionStatus="connecting" />
    );
    expect(screen.getByText('Connecting…')).toBeInTheDocument();
  });

  it('renders connector arrows between stages', () => {
    render(
      <PipelineStatus stage1="active" stage2="active" connectionStatus="connected" />
    );
    const connectors = screen.getAllByText('→');
    expect(connectors).toHaveLength(2);
  });
});
