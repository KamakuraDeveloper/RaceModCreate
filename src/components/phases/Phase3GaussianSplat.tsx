import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus } from '../../types/pipeline';
import StatusBadge from '../common/StatusBadge';
import PhaseProgress from '../pipeline/PhaseProgress';
import ParameterSlider from '../common/ParameterSlider';
import GaussianViewer from '../visualization/GaussianViewer';

function ToggleRow({ label, value, onChange, disabled }: { label: string; value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      onClick={() => !disabled && onChange(!value)}
      style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '8px 10px', width: '100%', textAlign: 'left',
        background: value ? 'rgba(0,255,136,0.06)' : 'rgba(255,255,255,0.02)',
        border: `1px solid ${value ? 'rgba(0,255,136,0.2)' : 'rgba(255,255,255,0.06)'}`,
        borderRadius: '3px', cursor: disabled ? 'not-allowed' : 'pointer',
      }}
    >
      <div style={{
        width: 10, height: 10, borderRadius: '2px',
        background: value ? '#00ff88' : 'transparent',
        border: `1px solid ${value ? '#00ff88' : '#444'}`,
        flexShrink: 0,
      }} />
      <span style={{ fontSize: '10px', color: value ? '#00ff88' : '#666', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em' }}>
        {label}
      </span>
    </button>
  );
}

export default function Phase3GaussianSplat() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.GAUSSIAN_SPLAT;
  const ps = state.phases[phase];
  const cfg = state.configs.gaussianSplat;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const update = (key: string, value: unknown) => {
    dispatch({ type: 'UPDATE_CONFIG', configKey: `gaussianSplat.${key}`, value });
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="3D Gaussian Splatting Training" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        TRAINING PARAMETERS
      </div>

      <ParameterSlider
        label="ITERATIONS"
        value={cfg.iterations}
        min={5000} max={100000} step={5000}
        onChange={v => update('iterations', v)}
        disabled={isLocked}
        tooltip="Total training iterations for Gaussian optimization"
      />

      <ParameterSlider
        label="LEARNING RATE"
        value={cfg.learningRate}
        min={0.0001} max={0.01} step={0.0001}
        onChange={v => update('learningRate', v)}
        disabled={isLocked}
        tooltip="Global learning rate for Gaussian parameters"
      />

      <ParameterSlider
        label="SH DEGREE"
        value={cfg.shDegree}
        min={0} max={4} step={1}
        onChange={v => update('shDegree', v)}
        disabled={isLocked}
        tooltip="Spherical harmonics degree for view-dependent color (0=diffuse, 3=glossy)"
      />

      <ParameterSlider
        label="MAX GAUSSIANS"
        value={cfg.maxGaussians}
        min={500000} max={5000000} step={100000}
        onChange={v => update('maxGaussians', v)}
        disabled={isLocked}
        tooltip="Maximum number of Gaussian primitives"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        DENSIFICATION & PRUNING
      </div>

      <ParameterSlider
        label="DENSIFY INTERVAL"
        value={cfg.densifyInterval}
        min={50} max={500} step={50}
        onChange={v => update('densifyInterval', v)}
        disabled={isLocked}
        tooltip="Interval (iterations) between densification steps"
      />

      <ParameterSlider
        label="SPLIT THRESHOLD"
        value={cfg.splitThreshold}
        min={0.01} max={0.2} step={0.01}
        onChange={v => update('splitThreshold', v)}
        disabled={isLocked}
        tooltip="Position gradient threshold for splitting Gaussians"
      />

      <ParameterSlider
        label="PRUNE THRESHOLD"
        value={cfg.pruneThreshold}
        min={0.001} max={0.05} step={0.001}
        onChange={v => update('pruneThreshold', v)}
        disabled={isLocked}
        tooltip="Minimum opacity below which Gaussians are pruned"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        LEARNING RATES
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
        <ParameterSlider
          label="POSITION LR"
          value={cfg.positionLR}
          min={0.00001} max={0.001} step={0.00001}
          onChange={v => update('positionLR', v)}
          disabled={isLocked}
          tooltip="Learning rate for Gaussian positions"
        />
        <ParameterSlider
          label="OPACITY LR"
          value={cfg.opacityLR}
          min={0.01} max={0.1} step={0.01}
          onChange={v => update('opacityLR', v)}
          disabled={isLocked}
          tooltip="Learning rate for Gaussian opacity"
        />
        <ParameterSlider
          label="SCALE LR"
          value={cfg.scaleLR}
          min={0.001} max={0.05} step={0.001}
          onChange={v => update('scaleLR', v)}
          disabled={isLocked}
          tooltip="Learning rate for Gaussian scale"
        />
      </div>

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        RENDERING OPTIONS
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <ToggleRow label="Mip-Splatting" value={cfg.mipSplatting} onChange={v => update('mipSplatting', v)} disabled={isLocked} />
        <ToggleRow label="Anti-Aliasing" value={cfg.antiAliasing} onChange={v => update('antiAliasing', v)} disabled={isLocked} />
      </div>

      <div style={{ marginTop: '16px' }}>
        <GaussianViewer />
      </div>
    </div>
  );
}
