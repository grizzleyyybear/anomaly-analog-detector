'use client';

import { useMemo } from 'react';
import { useAbly } from './hooks/useAbly';
import SignalChart from './components/SignalChart';
import MetricCard from './components/MetricCard';
import AnomalyLog from './components/AnomalyLog';
import PipelineStatus from './components/PipelineStatus';

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

export default function Home() {
  const {
    connectionStatus,
    signalHistory,
    currentSignal,
    anomalyStatus,
    anomalyLog,
    pipelineInfo,
    reconstructionError,
    threshold,
  } = useAbly();

  const stats = useMemo(() => computeStats(signalHistory), [signalHistory]);
  const isAnomaly = anomalyStatus.status === 'Anomaly Detected';
  const anomalyCount = anomalyLog.filter(e => e.status === 'Anomaly Detected').length;
  const errorPercent = reconstructionError != null && threshold != null
    ? ((reconstructionError / threshold) * 100).toFixed(1)
    : null;

  return (
    <main className="dashboard">
      <header className="dashboard__header">
        <div className="dashboard__title-group">
          <h1 className="dashboard__title">
            <span className="dashboard__title-icon">◈</span>
            Anomaly Analog Detector
          </h1>
          <p className="dashboard__subtitle">Real-Time Industrial Signal Monitoring</p>
        </div>
        <div className={`connection-badge connection-badge--${connectionStatus}`}>
          <span className="connection-badge__dot" />
          {connectionStatus === 'connected' ? 'Live' : connectionStatus}
        </div>
      </header>

      <PipelineStatus
        stage1={pipelineInfo.stage1}
        stage2={pipelineInfo.stage2}
        connectionStatus={connectionStatus}
      />

      <section className="dashboard__section">
        <h2 className="section-title">Signal Waveform</h2>
        <SignalChart data={signalHistory} anomalyLog={anomalyLog} />
      </section>

      <section className="dashboard__metrics">
        <MetricCard
          label="Current Signal"
          value={currentSignal ? currentSignal.value.toFixed(4) : '—'}
          variant="info"
          icon="⚡"
        />
        <MetricCard
          label="System Status"
          value={isAnomaly ? 'ANOMALY' : anomalyStatus.status === 'Waiting...' ? 'Waiting' : 'Normal'}
          variant={isAnomaly ? 'danger' : anomalyStatus.status === 'Waiting...' ? 'default' : 'success'}
          icon={isAnomaly ? '⚠' : '✓'}
        />
        <MetricCard
          label="Anomalies Detected"
          value={anomalyCount}
          variant={anomalyCount > 0 ? 'warning' : 'default'}
          icon="🔍"
          subtitle={`of ${anomalyLog.length} events`}
        />
        <MetricCard
          label="Data Points"
          value={stats.count}
          variant="default"
          icon="📊"
          subtitle="in buffer"
        />
      </section>

      <div className="dashboard__grid-2">
        <section className="dashboard__section">
          <h2 className="section-title">Signal Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Min</span>
              <span className="stat-value">{stats.min}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Max</span>
              <span className="stat-value">{stats.max}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Mean</span>
              <span className="stat-value">{stats.mean}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Std Dev</span>
              <span className="stat-value">{stats.stdDev}</span>
            </div>
          </div>
        </section>

        <section className="dashboard__section">
          <h2 className="section-title">Reconstruction Error</h2>
          {reconstructionError != null ? (
            <div className="error-gauge">
              <div className="error-gauge__values">
                <span>Current: <strong>{reconstructionError.toFixed(6)}</strong></span>
                <span>Threshold: <strong>{threshold?.toFixed(6) ?? '—'}</strong></span>
              </div>
              {errorPercent && (
                <div className="error-gauge__bar-wrapper">
                  <div
                    className={`error-gauge__bar ${parseFloat(errorPercent) > 100 ? 'error-gauge__bar--danger' : ''}`}
                    style={{ width: `${Math.min(parseFloat(errorPercent), 100)}%` }}
                  />
                </div>
              )}
              {errorPercent && <p className="error-gauge__percent">{errorPercent}% of threshold</p>}
            </div>
          ) : (
            <p className="text-muted">Waiting for reconstruction error data...</p>
          )}
        </section>
      </div>

      <AnomalyLog entries={anomalyLog} />

      <footer className="dashboard__footer">
        <p>Anomaly Analog Detector — Dual-ML Pipeline for Industrial Signal Monitoring</p>
      </footer>
    </main>
  );
}
