import { usePipeline } from '../../hooks/usePipeline';
import { PHASE_ORDER, PhaseStatus } from '../../types/pipeline';

function formatNum(n: number | undefined): string {
  if (n === undefined || n === 0) return '—';
  if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
}

export default function MetricsPanel() {
  const { state } = usePipeline();

  const totalTime = PHASE_ORDER.reduce((sum, p) => sum + state.phases[p].metrics.processingTime, 0);
  const peakMemory = Math.max(...PHASE_ORDER.map(p => state.phases[p].metrics.memoryUsage));
  const completedPhases = PHASE_ORDER.filter(p => state.phases[p].status === PhaseStatus.COMPLETED).length;

  // Aggregate metrics from all phases
  const m = Object.fromEntries(PHASE_ORDER.map(p => [p, state.phases[p].metrics]));

  const rows: [string, string, string][] = [
    ['TOTAL TIME', `${totalTime.toFixed(1)}s`, '#e0e0ff'],
    ['PEAK MEMORY', peakMemory > 0 ? `${peakMemory} MB` : '—', '#ffaa00'],
    ['PHASES DONE', `${completedPhases}/6`, '#00ff88'],
    ['FRAMES', formatNum(m.INGEST?.framesExtracted), '#00f0ff'],
    ['POINT CLOUD', formatNum(m.SFM?.pointCloudDensity), '#00f0ff'],
    ['FEATURES', formatNum(m.SFM?.featuresMatched), '#8888aa'],
    ['GAUSSIANS', formatNum(m.GAUSSIAN_SPLAT?.gaussianCount), '#ff00aa'],
    ['MESH FACES', formatNum(m.MESH?.meshFaces), '#ffaa00'],
    ['TEX RES', m.MESH?.textureResolution ?? '—', '#8888aa'],
    ['TRACK LEN', m.COURSE?.trackLength ? `${m.COURSE.trackLength}m` : '—', '#00ff88'],
    ['EXPORTS', formatNum(m.EXPORT?.exportedFormats), '#00f0ff'],
  ];

  return (
    <div style={{
      flex: 1,
      minHeight: '160px',
      background: '#0c0c14',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      <div style={{
        padding: '8px 14px',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        fontSize: '9px', color: '#555',
        fontFamily: 'var(--font-mono)', letterSpacing: '0.15em',
        flexShrink: 0,
      }}>
        METRICS
      </div>
      <div style={{ flex: 1, overflow: 'auto', padding: '8px 14px' }}>
        {rows.map(([label, value, color]) => (
          <div key={label} style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '4px 0',
            borderBottom: '1px solid rgba(255,255,255,0.02)',
          }}>
            <span style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em' }}>
              {label}
            </span>
            <span style={{ fontSize: '12px', color, fontFamily: 'var(--font-mono)', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
              {value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
