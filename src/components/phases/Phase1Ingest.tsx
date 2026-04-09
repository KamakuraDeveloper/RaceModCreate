import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus, HDRMode } from '../../types/pipeline';
import StatusBadge from '../common/StatusBadge';
import PhaseProgress from '../pipeline/PhaseProgress';
import ParameterSlider from '../common/ParameterSlider';
import ParameterInput from '../common/ParameterInput';

export default function Phase1Ingest() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.INGEST;
  const ps = state.phases[phase];
  const cfg = state.configs.ingest;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const update = (key: string, value: unknown) => {
    dispatch({ type: 'UPDATE_CONFIG', configKey: `ingest.${key}`, value });
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="Frame Extraction" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        INPUT SOURCE
      </div>

      <ParameterInput
        label="SOURCE FILE"
        value={cfg.sourceFile}
        onChange={v => update('sourceFile', v)}
        disabled={isLocked}
        tooltip="Insta360 .insv video file path"
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
        <ParameterInput
          label="OUTPUT WIDTH"
          value={cfg.outputResolution[0]}
          type="number"
          onChange={v => update('outputResolution', [parseInt(v) || 5760, cfg.outputResolution[1]])}
          disabled={isLocked}
          unit="px"
          tooltip="Equirectangular output width"
        />
        <ParameterInput
          label="OUTPUT HEIGHT"
          value={cfg.outputResolution[1]}
          type="number"
          onChange={v => update('outputResolution', [cfg.outputResolution[0], parseInt(v) || 2880])}
          disabled={isLocked}
          unit="px"
          tooltip="Equirectangular output height"
        />
      </div>

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        EXTRACTION PARAMETERS
      </div>

      <ParameterSlider
        label="FRAME RATE"
        value={cfg.frameRate}
        min={1} max={10} step={1}
        unit=" fps"
        onChange={v => update('frameRate', v)}
        disabled={isLocked}
        tooltip="Adaptive keyframe extraction rate (1-10 fps)"
      />

      <ParameterSlider
        label="DENOISE STRENGTH"
        value={cfg.denoiseStrength}
        min={0} max={1} step={0.05}
        onChange={v => update('denoiseStrength', v)}
        disabled={isLocked}
        tooltip="Temporal denoising strength"
      />

      <ParameterSlider
        label="EXPOSURE COMP"
        value={cfg.exposureCompensation}
        min={-3} max={3} step={0.5}
        unit=" EV"
        onChange={v => update('exposureCompensation', v)}
        disabled={isLocked}
        tooltip="Exposure compensation in EV stops"
      />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        PROCESSING OPTIONS
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <ToggleOption label="FlowState Stabilization" value={cfg.stabilization} onChange={v => update('stabilization', v)} disabled={isLocked} />
        <ToggleOption label="GPS Sync" value={cfg.gpsSync} onChange={v => update('gpsSync', v)} disabled={isLocked} />
        <ToggleOption label="IMU Sync" value={cfg.imuSync} onChange={v => update('imuSync', v)} disabled={isLocked} />
        <div>
          <label style={{ display: 'block', fontSize: '11px', color: '#8888aa', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em', marginBottom: '4px' }}>
            HDR MODE
          </label>
          <select
            value={cfg.hdrMode}
            onChange={e => update('hdrMode', e.target.value)}
            disabled={isLocked}
            style={{
              width: '100%', padding: '6px 8px',
              background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '3px', color: '#e0e0ff', fontSize: '11px', fontFamily: 'var(--font-mono)',
            }}
          >
            {Object.values(HDRMode).map(m => (
              <option key={m} value={m} style={{ background: '#1a1a2e' }}>{m.toUpperCase()}</option>
            ))}
          </select>
        </div>
      </div>

      <ParameterInput
        label="COLOR SPACE"
        value={cfg.colorSpace}
        onChange={v => update('colorSpace', v)}
        disabled={isLocked}
        tooltip="Output color space (sRGB, Linear, ACEScg)"
      />
    </div>
  );
}

function ToggleOption({ label, value, onChange, disabled }: { label: string; value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      onClick={() => !disabled && onChange(!value)}
      style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '8px 10px',
        background: value ? 'rgba(0,255,136,0.06)' : 'rgba(255,255,255,0.02)',
        border: `1px solid ${value ? 'rgba(0,255,136,0.2)' : 'rgba(255,255,255,0.06)'}`,
        borderRadius: '3px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        width: '100%',
        textAlign: 'left',
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
