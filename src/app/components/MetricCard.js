export default function MetricCard({ label, value, variant = 'default', icon, subtitle }) {
  const variants = {
    default: 'metric-card',
    success: 'metric-card metric-card--success',
    danger: 'metric-card metric-card--danger',
    warning: 'metric-card metric-card--warning',
    info: 'metric-card metric-card--info',
  };

  return (
    <div className={variants[variant] || variants.default}>
      {icon && <span className="metric-card__icon">{icon}</span>}
      <p className="metric-card__label">{label}</p>
      <p className="metric-card__value">
        {value}
      </p>
      {subtitle && <p className="metric-card__subtitle">{subtitle}</p>}
    </div>
  );
}
