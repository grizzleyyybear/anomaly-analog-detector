import { describe, it, expect } from 'vitest';

/**
 * Extracted from page.js for testability.
 * Mirrors the computeStats function used in the dashboard.
 */
function computeStats(history) {
  if (history.length === 0) return { min: '—', max: '—', mean: '—', stdDev: '—', count: 0 };

  const values = history.map(p => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);

  return {
    min: min.toFixed(4),
    max: max.toFixed(4),
    mean: mean.toFixed(4),
    stdDev: stdDev.toFixed(4),
    count: values.length,
  };
}

describe('computeStats', () => {
  it('returns dashes for empty history', () => {
    const stats = computeStats([]);
    expect(stats.min).toBe('—');
    expect(stats.max).toBe('—');
    expect(stats.mean).toBe('—');
    expect(stats.stdDev).toBe('—');
    expect(stats.count).toBe(0);
  });

  it('computes correct stats for single value', () => {
    const stats = computeStats([{ value: 5.0 }]);
    expect(stats.min).toBe('5.0000');
    expect(stats.max).toBe('5.0000');
    expect(stats.mean).toBe('5.0000');
    expect(stats.stdDev).toBe('0.0000');
    expect(stats.count).toBe(1);
  });

  it('computes correct stats for known values', () => {
    const history = [
      { value: 2.0 },
      { value: 4.0 },
      { value: 6.0 },
      { value: 8.0 },
    ];
    const stats = computeStats(history);
    expect(stats.min).toBe('2.0000');
    expect(stats.max).toBe('8.0000');
    expect(stats.mean).toBe('5.0000');
    expect(parseFloat(stats.stdDev)).toBeCloseTo(2.2361, 3);
    expect(stats.count).toBe(4);
  });

  it('handles negative values', () => {
    const history = [{ value: -3.0 }, { value: 1.0 }, { value: -1.0 }];
    const stats = computeStats(history);
    expect(stats.min).toBe('-3.0000');
    expect(stats.max).toBe('1.0000');
    expect(parseFloat(stats.mean)).toBeCloseTo(-1.0, 4);
  });
});
