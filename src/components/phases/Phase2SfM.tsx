import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus, FeatureMatcherType, FeatureType, CameraModel } from '../../types/pipeline';
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

export default function Phase2SfM() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.SFM;
  const ps = state.phases[phase];
  const cfg = state.configs.sfm;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const update = (key: string, value: unknown) => {
    dispatch({ type: 'UPDATE_CONFIG', configKey: `sfm.${key}`, value });
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="Structure from Motion" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        FEATURE MATCHING
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
        <SelectField
          label="FEATURE TYPE"
          value={cfg.featureType}
          options={Object.fromEntries(Object.values(FeatureType).map(v => [v, v.toUpperCase()]))}
          onChange={v => update('featureType', v)}
          disabled={isLocked}
          tooltip="Feature detector: SuperPoint (learned), SIFT, or ORB"
        />
        <SelectField
          label="MATCHER"
          value={cfg.matcher}
          options={Object.fromEntries(Object.values(FeatureMatcherType).map(v => [v, v.replace('_', ' ').toUpperCase()]))}
          onChange={v => update('matcher', v)}
          disabled={isLocked}
          tooltip="Feature matching algorithm"
        />
      </div>

      <SelectField
        label="CAMERA MODEL"
        value={cfg.cameraModel}
        options={Object.fromEntries(Object.values(CameraModel).map(v => [v, v.toUpperCase()]))}
        onChange={v => update('cameraModel', v)}
        disabled={isLocked}
        tooltip="Camera distortion model for 360° imagery"
      />

      <ParameterSlider
        label="MAX FEATURES / IMAGE"
        value={cfg.maxFeatures}
        min={1024} max={16384} step={1024}
        onChange={v => update('maxFeatures', v)}
        disabled={isLocked}
        tooltip="Maximum features detected per image"
      />

      <ParameterSlider
        label="MATCH RATIO"
        value={cfg.matchRatio}
        min={0.5} max={1.0} step={0.01}
        onChange={v => update('matchRatio', v)}
        disabled={isLocked}
        tooltip="Lowe's ratio test threshold"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        RECONSTRUCTION
      </div>

      <ParameterSlider
        label="MIN TRACK LENGTH"
        value={cfg.minTrackLength}
        min={2} max={10} step={1}
        onChange={v => update('minTrackLength', v)}
        disabled={isLocked}
        tooltip="Minimum number of images a 3D point must be visible in"
      />

      <ParameterSlider
        label="MAX REPROJ ERROR"
        value={cfg.filterMaxReprojError}
        min={1} max={10} step={0.5}
        unit=" px"
        onChange={v => update('filterMaxReprojError', v)}
        disabled={isLocked}
        tooltip="Maximum reprojection error for point filtering"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '8px' }}>
        <ToggleRow label="GPS Georeferencing" value={cfg.gpsGeoref} onChange={v => update('gpsGeoref', v)} disabled={isLocked} />
        <ToggleRow label="Bundle Adjustment" value={cfg.bundleAdjustment} onChange={v => update('bundleAdjustment', v)} disabled={isLocked} />
        <ToggleRow label="Robust Triangulation" value={cfg.robustTriangulation} onChange={v => update('robustTriangulation', v)} disabled={isLocked} />
      </div>
    </div>
  );
}
