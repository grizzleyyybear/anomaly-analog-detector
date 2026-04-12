export interface AnomalyEntry {
  status: string;
  timestamp: string;
  time: string;
  reconstructionError: number | null;
}

export interface AnomalyLogProps {
  entries: AnomalyEntry[];
}

export default function AnomalyLog({ entries }: AnomalyLogProps) {
  if (!entries || entries.length === 0) {
    return (
      <div className="anomaly-log">
        <h3 className="anomaly-log__title">Event Log</h3>
        <p className="anomaly-log__empty">No events recorded yet. Waiting for data...</p>
      </div>
    );
  }

  return (
    <section className="anomaly-log" aria-label="Anomaly event log">
      <h3 className="anomaly-log__title">Event Log</h3>
      <div className="anomaly-log__list" role="log" aria-live="polite">
        {entries.map((entry, i) => (
          <div
            key={`${entry.timestamp}-${i}`}
            className={`anomaly-log__entry ${
              entry.status === 'Anomaly Detected'
                ? 'anomaly-log__entry--anomaly'
                : 'anomaly-log__entry--normal'
            }`}
            role="article"
            aria-label={`${entry.status} at ${entry.time}`}
          >
            <span className="anomaly-log__time">{entry.time}</span>
            <span className="anomaly-log__status">{entry.status}</span>
            {entry.reconstructionError != null && (
              <span className="anomaly-log__error">
                err: {entry.reconstructionError.toFixed(6)}
              </span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
