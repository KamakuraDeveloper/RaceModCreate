import type { PipelinePhase } from '../../types/pipeline';
import { PhaseStatus, PHASE_LABELS } from '../../types/pipeline';
import { usePipeline } from '../../hooks/usePipeline';

export default function PipelineControls({ phase }: { phase: PipelinePhase }) {
  const { state, runPhase, pauseCurrentPhase, runAll, stopAll, resetPipeline } = usePipeline();
  const ps = state.phases[phase];

  const btnBase: React.CSSProperties = {
    padding: '8px 16px',
    border: '1px solid',
    borderRadius: '3px',
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    fontWeight: 700,
    letterSpacing: '0.08em',
    cursor: 'pointer',
    transition: 'all 0.15s',
    background: 'transparent',
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 20px',
      background: 'rgba(0,0,0,0.3)',
    }}>
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <span style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', marginRight: '8px' }}>
          {PHASE_LABELS[phase]}
        </span>
        {ps.status !== PhaseStatus.RUNNING ? (
          <button
            onClick={() => runPhase(phase)}
            style={{ ...btnBase, borderColor: '#00ff88', color: '#00ff88' }}
          >
            ▶ START
          </button>
        ) : (
          <button
            onClick={() => pauseCurrentPhase(phase)}
            style={{ ...btnBase, borderColor: '#ffaa00', color: '#ffaa00' }}
          >
            ❚❚ PAUSE
          </button>
        )}
      </div>
      <div style={{ display: 'flex', gap: '8px' }}>
        <button onClick={runAll} style={{ ...btnBase, borderColor: '#00f0ff', color: '#00f0ff' }}>
          ⏩ RUN ALL
        </button>
        <button onClick={stopAll} style={{ ...btnBase, borderColor: '#ff003c', color: '#ff003c' }}>
          ⏹ STOP
        </button>
        <button onClick={resetPipeline} style={{ ...btnBase, borderColor: '#555', color: '#666' }}>
          ↺ RESET
        </button>
      </div>
    </div>
  );
}
