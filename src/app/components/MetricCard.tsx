export interface MetricCardProps {
  label: string;
  value: string | number;
  variant?: 'default' | 'success' | 'danger' | 'warning' | 'info';
  icon?: string;
  subtitle?: string;
}

export default function MetricCard({ label, value, variant = 'default', icon, subtitle }: MetricCardProps) {
  const variants: Record<string, string> = {
    default: 'metric-card',
    success: 'metric-card metric-card--success',
    danger: 'metric-card metric-card--danger',
    warning: 'metric-card metric-card--warning',
    info: 'metric-card metric-card--info',
  };

  return (
    <div className={variants[variant] || variants.default} role="status" aria-label={label}>
      {icon && <span className="metric-card__icon" aria-hidden="true">{icon}</span>}
      <p className="metric-card__label">{label}</p>
      <p className="metric-card__value" aria-live="polite">
        {value}
      </p>
      {subtitle && <p className="metric-card__subtitle">{subtitle}</p>}
    </div>
  );
}
