import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus, SegmentationModel, SurfaceMaterial } from '../../types/pipeline';
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

export default function Phase5Course() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.COURSE;
  const ps = state.phases[phase];
  const cfg = state.configs.course;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const update = (key: string, value: unknown) => {
    dispatch({ type: 'UPDATE_CONFIG', configKey: `course.${key}`, value });
  };

  const allMaterials = Object.values(SurfaceMaterial);

  const toggleMaterial = (mat: string) => {
    const current = cfg.surfaceMaterials as string[];
    const next = current.includes(mat) ? current.filter(m => m !== mat) : [...current, mat];
    update('surfaceMaterials', next);
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="Course Construction" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        SEGMENTATION
      </div>

      <SelectField
        label="SEGMENTATION MODEL"
        value={cfg.segmentationModel}
        options={Object.fromEntries(Object.values(SegmentationModel).map(v => [v, v.toUpperCase()]))}
        onChange={v => update('segmentationModel', v)}
        disabled={isLocked}
        tooltip="Semantic segmentation model for road detection"
      />

      <ParameterSlider
        label="ROAD DETECTION THRESHOLD"
        value={cfg.roadDetectionThreshold}
        min={0.5} max={1.0} step={0.01}
        onChange={v => update('roadDetectionThreshold', v)}
        disabled={isLocked}
        tooltip="Confidence threshold for road surface classification"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        SURFACE MATERIALS
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '12px' }}>
        {allMaterials.map(mat => {
          const active = (cfg.surfaceMaterials as string[]).includes(mat);
          return (
            <button
              key={mat}
              onClick={() => !isLocked && toggleMaterial(mat)}
              style={{
                padding: '4px 10px',
                fontSize: '9px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                letterSpacing: '0.08em',
                background: active ? 'rgba(0,240,255,0.1)' : 'rgba(255,255,255,0.02)',
                border: `1px solid ${active ? '#00f0ff' : 'rgba(255,255,255,0.06)'}`,
                borderRadius: '2px',
                color: active ? '#00f0ff' : '#555',
                cursor: isLocked ? 'not-allowed' : 'pointer',
                textTransform: 'uppercase',
              }}
            >
              {mat.replace('_', ' ')}
            </button>
          );
        })}
      </div>

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        TRACK GEOMETRY
      </div>

      <ParameterSlider
        label="TRACK WIDTH"
        value={cfg.trackWidth}
        min={4} max={20} step={0.5}
        unit=" m"
        onChange={v => update('trackWidth', v)}
        disabled={isLocked}
        tooltip="Average track width in meters"
      />

      <ParameterSlider
        label="ELEVATION SAMPLING"
        value={cfg.elevationSampling}
        min={0.25} max={5.0} step={0.25}
        unit=" m"
        onChange={v => update('elevationSampling', v)}
        disabled={isLocked}
        tooltip="Elevation sampling interval in meters"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        DETECTION OPTIONS
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <ToggleRow label="Grip Map" value={cfg.gripMap} onChange={v => update('gripMap', v)} disabled={isLocked} />
        <ToggleRow label="Racing Line" value={cfg.racingLineDetection} onChange={v => update('racingLineDetection', v)} disabled={isLocked} />
        <ToggleRow label="Camber Detection" value={cfg.camberDetection} onChange={v => update('camberDetection', v)} disabled={isLocked} />
        <ToggleRow label="Barrier Detection" value={cfg.barrierDetection} onChange={v => update('barrierDetection', v)} disabled={isLocked} />
        <ToggleRow label="Pit Lane" value={cfg.pitLaneDetection} onChange={v => update('pitLaneDetection', v)} disabled={isLocked} />
      </div>
    </div>
  );
}
