export interface PipelineStatusProps {
  stage1: string | null;
  stage2: string | null;
  connectionStatus: string | null;
}

export default function PipelineStatus({ stage1, stage2, connectionStatus }: PipelineStatusProps) {
  const getStatusDot = (status: string | null): string => {
    if (status === 'active' || status === 'connected') return 'status-dot status-dot--active';
    if (status === 'idle' || status === 'connecting') return 'status-dot status-dot--idle';
    return 'status-dot status-dot--error';
  };

  const getStatusLabel = (status: string | null): string => {
    if (!status) return 'Unknown';
    const labels: Record<string, string> = {
      active: 'Active',
      idle: 'Idle',
      connected: 'Connected',
      connecting: 'Connecting…',
      disconnected: 'Disconnected',
    };
    return labels[status] || status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <nav className="pipeline-status" aria-label="Pipeline status">
      <h3 className="pipeline-status__title">Pipeline Status</h3>
      <div className="pipeline-status__stages" role="list">
        <div className="pipeline-stage" role="listitem">
          <span className={getStatusDot(connectionStatus)} aria-hidden="true" />
          <div>
            <p className="pipeline-stage__name">Connection</p>
            <p className="pipeline-stage__label" aria-live="polite">{getStatusLabel(connectionStatus)}</p>
          </div>
        </div>
        <div className="pipeline-connector" aria-hidden="true">→</div>
        <div className="pipeline-stage" role="listitem">
          <span className={getStatusDot(stage1)} aria-hidden="true" />
          <div>
            <p className="pipeline-stage__name">Stage 1</p>
            <p className="pipeline-stage__label">ADC Corrector</p>
          </div>
        </div>
        <div className="pipeline-connector" aria-hidden="true">→</div>
        <div className="pipeline-stage" role="listitem">
          <span className={getStatusDot(stage2)} aria-hidden="true" />
          <div>
            <p className="pipeline-stage__name">Stage 2</p>
            <p className="pipeline-stage__label">LSTM Autoencoder</p>
          </div>
        </div>
      </div>
    </nav>
  );
}
