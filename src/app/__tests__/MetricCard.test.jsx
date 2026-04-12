import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MetricCard from '../components/MetricCard.jsx';

describe('MetricCard', () => {
  it('renders label and value', () => {
    render(<MetricCard label="Test Label" value="42" icon="⚡" />);
    expect(screen.getByText('Test Label')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('applies danger variant class', () => {
    const { container } = render(
      <MetricCard label="Status" value="ANOMALY" variant="danger" icon="⚠" />
    );
    const card = container.querySelector('.metric-card');
    expect(card.className).toContain('metric-card--danger');
  });

  it('renders subtitle when provided', () => {
    render(<MetricCard label="Count" value="5" icon="🔍" subtitle="of 10 events" />);
    expect(screen.getByText('of 10 events')).toBeInTheDocument();
  });

  it('renders without subtitle', () => {
    const { container } = render(<MetricCard label="Count" value="5" icon="📊" />);
    expect(container.querySelector('.metric-card__subtitle')).toBeNull();
  });
});
