export default function PipelineStatus({ stage1, stage2, connectionStatus }) {
  const getStatusDot = (status) => {
    if (status === 'active' || status === 'connected') return 'status-dot status-dot--active';
    if (status === 'idle' || status === 'connecting') return 'status-dot status-dot--idle';
    return 'status-dot status-dot--error';
  };

  const getStatusLabel = (status) => {
    const labels = {
      active: 'Active',
      idle: 'Idle',
      connected: 'Connected',
      connecting: 'Connecting…',
      disconnected: 'Disconnected',
    };
    return labels[status] || status.charAt(0).toUpperCase() + status.slice(1);
  };

  return (
    <div className="pipeline-status">
      <h3 className="pipeline-status__title">Pipeline Status</h3>
      <div className="pipeline-status__stages">
        <div className="pipeline-stage">
          <span className={getStatusDot(connectionStatus)} />
          <div>
            <p className="pipeline-stage__name">Connection</p>
            <p className="pipeline-stage__label">{getStatusLabel(connectionStatus)}</p>
          </div>
        </div>
        <div className="pipeline-connector">→</div>
        <div className="pipeline-stage">
          <span className={getStatusDot(stage1)} />
          <div>
            <p className="pipeline-stage__name">Stage 1</p>
            <p className="pipeline-stage__label">ADC Corrector</p>
          </div>
        </div>
        <div className="pipeline-connector">→</div>
        <div className="pipeline-stage">
          <span className={getStatusDot(stage2)} />
          <div>
            <p className="pipeline-stage__name">Stage 2</p>
            <p className="pipeline-stage__label">LSTM Autoencoder</p>
          </div>
        </div>
      </div>
    </div>
  );
}
