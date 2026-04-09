import type { PhaseStatus } from '../../types/pipeline';

const STATUS_COLOR: Record<string, string> = {
  IDLE: '#333',
  QUEUED: '#ffaa00',
  RUNNING: '#00f0ff',
  PAUSED: '#ffaa00',
  COMPLETED: '#00ff88',
  ERROR: '#ff003c',
};

interface PhaseProgressProps {
  progress: number;
  status: PhaseStatus;
  label?: string;
  estimatedTimeRemaining?: number | null;
}

export default function PhaseProgress({ progress, status, label, estimatedTimeRemaining }: PhaseProgressProps) {
  const color = STATUS_COLOR[status] ?? '#333';
  return (
    <div style={{ marginBottom: '12px' }}>
      {label && (
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <span style={{ fontSize: '10px', color: '#666', fontFamily: 'var(--font-mono)' }}>{label}</span>
          <span style={{ fontSize: '10px', color, fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums' }}>
            {Math.round(progress)}%
            {estimatedTimeRemaining != null && estimatedTimeRemaining > 0 && ` • ~${Math.ceil(estimatedTimeRemaining)}s`}
          </span>
        </div>
      )}
      <div style={{
        width: '100%', height: '4px',
        background: 'rgba(255,255,255,0.06)',
        borderRadius: '2px', overflow: 'hidden',
      }}>
        <div style={{
          width: `${progress}%`, height: '100%',
          background: color,
          borderRadius: '2px',
          transition: 'width 0.3s ease',
          boxShadow: status === 'RUNNING' ? `0 0 8px ${color}` : 'none',
        }} />
      </div>
    </div>
  );
}
