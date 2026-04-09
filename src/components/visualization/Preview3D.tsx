import { usePipeline } from '../../hooks/usePipeline';

export default function Preview3D() {
  const { state } = usePipeline();
  const c = state.course;

  return (
    <div style={{
      flex: 1,
      minHeight: '200px',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(180deg, #0a0a14 0%, #0d0d1a 50%, #0a0a14 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Header */}
      <div style={{
        padding: '8px 14px',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        fontSize: '9px', color: '#555',
        fontFamily: 'var(--font-mono)', letterSpacing: '0.15em',
        flexShrink: 0,
      }}>
        3D PREVIEW
      </div>

      {/* Canvas area */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative',
      }}>
        {/* Grid overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage:
            'linear-gradient(rgba(0,240,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.03) 1px, transparent 1px)',
          backgroundSize: '40px 40px',
          opacity: 0.5,
        }} />

        {/* Course outline placeholder */}
        <div style={{ textAlign: 'center', position: 'relative', zIndex: 1 }}>
          <svg width="200" height="120" viewBox="0 0 200 120" fill="none">
            <path
              d="M30 90 Q30 30 70 30 Q120 30 130 60 Q140 90 170 80 Q190 70 170 40 Q150 20 100 20 Q50 20 30 50 Q20 70 30 90Z"
              stroke="rgba(0,240,255,0.3)" strokeWidth="2" fill="none"
              strokeDasharray="4 4"
            />
            <circle cx="30" cy="90" r="4" fill="#00ff88" />
            <text x="30" y="108" textAnchor="middle" fill="#00ff88" fontSize="8" fontFamily="monospace">START</text>
          </svg>
          <div style={{ marginTop: '8px', fontSize: '14px', color: '#00f0ff', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
            {c.name}
          </div>
          <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
            {c.length}m • {c.turns} turns • {c.elevation}m elevation
          </div>
          <div style={{ fontSize: '9px', color: '#333', fontFamily: 'var(--font-mono)', marginTop: '8px', fontStyle: 'italic' }}>
            WebGL viewer loads after mesh generation
          </div>
        </div>
      </div>
    </div>
  );
}
