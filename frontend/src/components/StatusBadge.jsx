const styles = {
  pending: 'border-sand/30 bg-sand/10 text-sand',
  approved: 'border-mint/30 bg-mint/10 text-mint',
  rejected: 'border-rose/30 bg-rose/10 text-rose',
  failed: 'border-rose/30 bg-rose/10 text-rose',
  anomaly: 'border-sand/30 bg-sand/10 text-sand',
}

export default function StatusBadge({ value, anomalyFlag = false }) {
  const key = anomalyFlag && value === 'pending' ? 'anomaly' : value
  return (
    <span className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${styles[key] || styles.pending}`}>
      {anomalyFlag && value === 'pending' ? 'anomaly' : value}
    </span>
  )
}
