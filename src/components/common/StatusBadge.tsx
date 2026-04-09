import type { PhaseStatus } from '../../types/pipeline';

const STATUS_STYLES: Record<string, { bg: string; color: string; label: string; glow?: string }> = {
  IDLE: { bg: 'rgba(255,255,255,0.06)', color: '#666', label: 'IDLE' },
  QUEUED: { bg: 'rgba(255,170,0,0.15)', color: '#ffaa00', label: 'QUEUED' },
  RUNNING: { bg: 'rgba(0,240,255,0.15)', color: '#00f0ff', label: 'RUNNING', glow: '0 0 8px rgba(0,240,255,0.4)' },
  PAUSED: { bg: 'rgba(255,170,0,0.15)', color: '#ffaa00', label: 'PAUSED' },
  COMPLETED: { bg: 'rgba(0,255,136,0.15)', color: '#00ff88', label: 'COMPLETE', glow: '0 0 8px rgba(0,255,136,0.3)' },
  ERROR: { bg: 'rgba(255,0,60,0.2)', color: '#ff003c', label: 'ERROR', glow: '0 0 8px rgba(255,0,60,0.4)' },
};

export default function StatusBadge({ status }: { status: PhaseStatus }) {
  const s = STATUS_STYLES[status] ?? STATUS_STYLES.IDLE;
  return (
    <span style={{
      display: 'inline-block',
      padding: '2px 10px',
      fontSize: '10px',
      fontWeight: 700,
      letterSpacing: '0.1em',
      fontFamily: 'var(--font-mono)',
      background: s.bg,
      color: s.color,
      border: `1px solid ${s.color}`,
      borderRadius: '2px',
      boxShadow: s.glow ?? 'none',
      textTransform: 'uppercase',
    }}>
      {s.label}
    </span>
  );
}
