import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus, MeshMethod, UVMethod } from '../../types/pipeline';
import StatusBadge from '../common/StatusBadge';
import PhaseProgress from '../pipeline/PhaseProgress';
import ParameterSlider from '../common/ParameterSlider';

function SelectField({ label, value, options, onChange, disabled, tooltip }: {
  label: string; value: string; options: Record<string, string>; onChange: (v: string) => void; disabled?: boolean; tooltip?: string;
}) {
  return (
    <div style={{ marginBottom: '10px' }} title={tooltip}>
      <label style={{ display: 'block', fontSize: '11px', color: '#8888aa', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em', marginBottom: '4px' }}>
        {label}
      </label>
      <select
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
        style={{
          width: '100%', padding: '6px 8px',
          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '3px', color: '#e0e0ff', fontSize: '11px', fontFamily: 'var(--font-mono)',
        }}
      >
        {Object.entries(options).map(([k, v]) => (
          <option key={k} value={k} style={{ background: '#1a1a2e' }}>{v}</option>
        ))}
      </select>
    </div>
  );
}

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

export default function Phase4Mesh() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.MESH;
  const ps = state.phases[phase];
  const cfg = state.configs.mesh;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const update = (key: string, value: unknown) => {
    dispatch({ type: 'UPDATE_CONFIG', configKey: `mesh.${key}`, value });
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="Mesh Conversion" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        EXTRACTION METHOD
      </div>

      <SelectField
        label="MESH METHOD"
        value={cfg.method}
        options={{
          [MeshMethod.SUGAR]: 'SuGaR (Gaussian → Mesh)',
          [MeshMethod.TWO_DGS]: '2DGS (2D Gaussian Surfels)',
          [MeshMethod.POISSON]: 'Poisson Surface Reconstruction',
        }}
        onChange={v => update('method', v)}
        disabled={isLocked}
        tooltip="Surface extraction algorithm"
      />

      <SelectField
        label="UV METHOD"
        value={cfg.uvMethod}
        options={Object.fromEntries(Object.values(UVMethod).map(v => [v, v.replace('_', ' ').toUpperCase()]))}
        onChange={v => update('uvMethod', v)}
        disabled={isLocked}
        tooltip="UV unwrapping algorithm"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        TEXTURE & QUALITY
      </div>

      <ParameterSlider
        label="TEXTURE RESOLUTION"
        value={cfg.textureResolution}
        min={1024} max={8192} step={1024}
        unit=" px"
        onChange={v => update('textureResolution', v)}
        disabled={isLocked}
        tooltip="Texture atlas resolution (4096 or 8192 recommended)"
      />

      <ParameterSlider
        label="LOD LEVELS"
        value={cfg.lodLevels}
        min={1} max={5} step={1}
        onChange={v => update('lodLevels', v)}
        disabled={isLocked}
        tooltip="Number of Level-of-Detail meshes to generate"
      />

      <ParameterSlider
        label="DECIMATION RATIO"
        value={cfg.decimationRatio}
        min={0.1} max={1.0} step={0.1}
        onChange={v => update('decimationRatio', v)}
        disabled={isLocked}
        tooltip="Target decimation ratio (0.5 = keep 50% of faces)"
      />

      <ParameterSlider
        label="SMOOTHING ITERATIONS"
        value={cfg.smoothingIterations}
        min={0} max={10} step={1}
        onChange={v => update('smoothingIterations', v)}
        disabled={isLocked}
        tooltip="Laplacian smoothing passes"
      />

      <ParameterSlider
        label="ISLAND MARGIN"
        value={cfg.islandMargin}
        min={0} max={16} step={1}
        unit=" px"
        onChange={v => update('islandMargin', v)}
        disabled={isLocked}
        tooltip="UV island padding in pixels"
      />

      <ParameterSlider
        label="MAX TEXTURE COUNT"
        value={cfg.maxTextureCount}
        min={1} max={16} step={1}
        onChange={v => update('maxTextureCount', v)}
        disabled={isLocked}
        tooltip="Maximum number of texture atlas pages"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        MAP GENERATION
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <ToggleRow label="Normal Map" value={cfg.generateNormalMap} onChange={v => update('generateNormalMap', v)} disabled={isLocked} />
        <ToggleRow label="Ambient Occlusion Map" value={cfg.generateAOMap} onChange={v => update('generateAOMap', v)} disabled={isLocked} />
      </div>
    </div>
  );
}
