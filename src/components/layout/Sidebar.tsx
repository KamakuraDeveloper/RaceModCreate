import { usePipeline } from '../../hooks/usePipeline';
import { PHASE_ORDER, PHASE_LABELS, PhaseStatus } from '../../types/pipeline';
import ProgressRing from '../common/ProgressRing';

const STATUS_COLOR: Record<string, string> = {
  IDLE: '#333',
  QUEUED: '#ffaa00',
  RUNNING: '#00f0ff',
  PAUSED: '#ffaa00',
  COMPLETED: '#00ff88',
  ERROR: '#ff003c',
};

export default function Sidebar() {
  const { state, setActivePhase } = usePipeline();

  return (
    <aside style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '2px',
      padding: '12px 0',
      background: '#0d0d14',
      borderRight: '1px solid rgba(255,255,255,0.04)',
      minWidth: '220px',
      overflowY: 'auto',
    }}>
      <div style={{ padding: '0 16px 12px', fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.15em' }}>
        PIPELINE PHASES
      </div>
      {PHASE_ORDER.map((phase) => {
        const ps = state.phases[phase];
        const isActive = state.activePhase === phase;
        const color = STATUS_COLOR[ps.status] ?? '#333';
        return (
          <button
            key={phase}
            onClick={() => setActivePhase(phase)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 16px',
              background: isActive ? 'rgba(0,240,255,0.06)' : 'transparent',
              border: 'none',
              borderLeft: isActive ? '2px solid #00f0ff' : '2px solid transparent',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
              textAlign: 'left',
            }}
          >
            <ProgressRing progress={ps.progress} size={32} strokeWidth={2} color={color} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: isActive ? '#e0e0ff' : '#888',
                letterSpacing: '0.05em',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}>
                {PHASE_LABELS[phase]}
              </div>
              <div style={{
                fontSize: '9px',
                fontFamily: 'var(--font-mono)',
                color: color,
                marginTop: '2px',
                letterSpacing: '0.1em',
              }}>
                {ps.status}{ps.status === PhaseStatus.RUNNING ? ` ${Math.round(ps.progress)}%` : ''}
              </div>
            </div>
          </button>
        );
      })}

      {/* Course info */}
      <div style={{ marginTop: 'auto', padding: '16px', borderTop: '1px solid rgba(255,255,255,0.04)' }}>
        <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.15em', marginBottom: '8px' }}>
          COURSE DATA
        </div>
        <div style={{ fontSize: '12px', color: '#00f0ff', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
          {state.course.name}
        </div>
        <div style={{ fontSize: '10px', color: '#666', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
          {state.course.length}m • {state.course.turns} turns
        </div>
        <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
          {state.course.location.lat.toFixed(4)}°N, {state.course.location.lng.toFixed(4)}°E
        </div>
        <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', marginTop: '2px' }}>
          ALT {state.course.elevation}m • {state.course.country}
        </div>
      </div>
    </aside>
  );
}
