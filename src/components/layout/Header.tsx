import { usePipeline } from '../../hooks/usePipeline';
import { PhaseStatus, PHASE_ORDER } from '../../types/pipeline';

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}

export default function Header() {
  const { state } = usePipeline();

  const runningCount = PHASE_ORDER.filter(p => state.phases[p].status === PhaseStatus.RUNNING).length;
  const completedCount = PHASE_ORDER.filter(p => state.phases[p].status === PhaseStatus.COMPLETED).length;

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 24px',
      background: 'linear-gradient(180deg, #12121a 0%, #0e0e16 100%)',
      borderBottom: '1px solid rgba(0,240,255,0.1)',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
          <span style={{
            fontSize: '22px', fontWeight: 900, letterSpacing: '0.08em',
            fontFamily: 'var(--font-mono)',
            background: 'linear-gradient(135deg, #00f0ff 0%, #ff00aa 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            TRACK
          </span>
          <span style={{ fontSize: '22px', fontWeight: 900, color: '#555', fontFamily: 'var(--font-mono)' }}>::</span>
          <span style={{
            fontSize: '22px', fontWeight: 900, letterSpacing: '0.08em',
            fontFamily: 'var(--font-mono)',
            background: 'linear-gradient(135deg, #ff00aa 0%, #ffaa00 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            FORGE
          </span>
        </div>
        <span style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>
          360° → RACE MOD PIPELINE
        </span>
      </div>

      {/* Status indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
        {/* Course name */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>COURSE</div>
          <div style={{ fontSize: '13px', color: '#00f0ff', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{state.course.name}</div>
        </div>

        {/* Elapsed */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>ELAPSED</div>
          <div style={{ fontSize: '13px', color: '#e0e0ff', fontFamily: 'var(--font-mono)', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
            {formatTime(state.totalElapsed)}
          </div>
        </div>

        {/* Running / Complete */}
        <div style={{ display: 'flex', gap: '16px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>ACTIVE</div>
            <div style={{ fontSize: '16px', fontWeight: 900, color: runningCount > 0 ? '#00f0ff' : '#333', fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums' }}>
              {runningCount}
            </div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em' }}>DONE</div>
            <div style={{ fontSize: '16px', fontWeight: 900, color: completedCount > 0 ? '#00ff88' : '#333', fontFamily: 'var(--font-mono)', fontVariantNumeric: 'tabular-nums' }}>
              {completedCount}/6
            </div>
          </div>
        </div>

        {/* System indicators */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: state.isRunning ? '#00ff88' : '#333', boxShadow: state.isRunning ? '0 0 8px #00ff88' : 'none' }} />
          <span style={{ fontSize: '10px', color: state.isRunning ? '#00ff88' : '#555', fontFamily: 'var(--font-mono)' }}>
            {state.isRunning ? 'PROCESSING' : 'STANDBY'}
          </span>
        </div>
      </div>
    </header>
  );
}
