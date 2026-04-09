import type { PipelinePhase } from '../../types/pipeline';
import { PHASE_LABELS } from '../../types/pipeline';
import { usePipeline } from '../../hooks/usePipeline';
import StatusBadge from '../common/StatusBadge';
import ProgressRing from '../common/ProgressRing';

export default function PhaseCard({ phase }: { phase: PipelinePhase }) {
  const { state } = usePipeline();
  const ps = state.phases[phase];

  return (
    <div style={{
      padding: '12px 16px',
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.04)',
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    }}>
      <ProgressRing progress={ps.progress} size={40} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#ccc', letterSpacing: '0.05em' }}>
          {PHASE_LABELS[phase]}
        </div>
        <div style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: '#666', marginTop: '2px' }}>
          {ps.duration > 0 ? `${ps.duration.toFixed(1)}s` : '—'}
        </div>
      </div>
      <StatusBadge status={ps.status} />
    </div>
  );
}
