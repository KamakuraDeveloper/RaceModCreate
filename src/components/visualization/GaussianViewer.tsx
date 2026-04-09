import { usePipeline } from '../../hooks/usePipeline';

export default function GaussianViewer() {
  const { state } = usePipeline();
  const gs = state.phases.GAUSSIAN_SPLAT;

  return (
    <div style={{
      padding: '16px',
      background: 'rgba(255,255,255,0.02)',
      border: '1px solid rgba(255,255,255,0.04)',
      borderRadius: '4px',
    }}>
      <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.15em', marginBottom: '12px' }}>
        GAUSSIAN SPLAT VIEWER
      </div>
      <div style={{
        height: '120px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'linear-gradient(135deg, rgba(255,0,170,0.05) 0%, rgba(0,240,255,0.05) 100%)',
        border: '1px dashed rgba(255,255,255,0.06)',
        borderRadius: '4px',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '20px', color: '#ff00aa', fontFamily: 'var(--font-mono)', fontWeight: 900 }}>
            {gs.metrics.gaussianCount ? (gs.metrics.gaussianCount / 1000000).toFixed(2) + 'M' : '—'}
          </div>
          <div style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
            GAUSSIAN PRIMITIVES
          </div>
          <div style={{ fontSize: '8px', color: '#333', fontFamily: 'var(--font-mono)', marginTop: '8px', fontStyle: 'italic' }}>
            WebGL splat renderer pending
          </div>
        </div>
      </div>
    </div>
  );
}
