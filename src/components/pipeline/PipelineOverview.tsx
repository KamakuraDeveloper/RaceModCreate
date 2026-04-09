import { usePipeline } from '../../hooks/usePipeline';
import { PHASE_ORDER, PHASE_SHORT, PhaseStatus } from '../../types/pipeline';

const STATUS_COLOR: Record<string, string> = {
  IDLE: '#333',
  QUEUED: '#ffaa00',
  RUNNING: '#00f0ff',
  PAUSED: '#ffaa00',
  COMPLETED: '#00ff88',
  ERROR: '#ff003c',
};

export default function PipelineOverview() {
  const { state, setActivePhase } = usePipeline();

  return (
    <div>
      <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.15em', marginBottom: '10px' }}>
        PIPELINE FLOW
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0' }}>
        {PHASE_ORDER.map((phase, i) => {
          const ps = state.phases[phase];
          const color = STATUS_COLOR[ps.status] ?? '#333';
          const isActive = state.activePhase === phase;
          return (
            <div key={phase} style={{ display: 'flex', alignItems: 'center', flex: 1 }}>
              <button
                onClick={() => setActivePhase(phase)}
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 4px',
                  background: isActive ? 'rgba(0,240,255,0.06)' : 'transparent',
                  border: `1px solid ${isActive ? 'rgba(0,240,255,0.2)' : 'rgba(255,255,255,0.04)'}`,
                  borderRadius: '4px',
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Progress bar background */}
                <div style={{
                  position: 'absolute', bottom: 0, left: 0,
                  width: `${ps.progress}%`, height: '2px',
                  background: color,
                  transition: 'width 0.3s ease',
                  boxShadow: ps.status === PhaseStatus.RUNNING ? `0 0 8px ${color}` : 'none',
                }} />
                <div style={{
                  fontSize: '10px', fontWeight: 700,
                  fontFamily: 'var(--font-mono)',
                  color: color, letterSpacing: '0.05em',
                }}>
                  {PHASE_SHORT[phase]}
                </div>
                <div style={{
                  fontSize: '14px', fontWeight: 900,
                  fontFamily: 'var(--font-mono)',
                  color: ps.status === PhaseStatus.RUNNING ? '#fff' : color,
                  fontVariantNumeric: 'tabular-nums',
                }}>
                  {Math.round(ps.progress)}%
                </div>
              </button>
              {i < PHASE_ORDER.length - 1 && (
                <div style={{
                  width: '20px', height: '1px',
                  background: state.phases[PHASE_ORDER[i + 1]].status !== PhaseStatus.IDLE
                    ? 'rgba(0,240,255,0.3)' : 'rgba(255,255,255,0.06)',
                  flexShrink: 0,
                }} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
