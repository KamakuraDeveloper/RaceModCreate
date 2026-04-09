import { usePipeline } from '../../hooks/usePipeline';
import { PipelinePhase, PHASE_LABELS, PhaseStatus } from '../../types/pipeline';
import StatusBadge from '../common/StatusBadge';
import PhaseProgress from '../pipeline/PhaseProgress';
import { SIM_FORMATS } from '../../config/simFormats';
import type { ExportConfig, SimFormatConfig } from '../../types/pipeline';

export default function Phase6Export() {
  const { state, dispatch } = usePipeline();
  const phase = PipelinePhase.EXPORT;
  const ps = state.phases[phase];
  const cfg = state.configs.export;
  const isLocked = ps.status === PhaseStatus.RUNNING;

  const updateFormat = (formatId: string, key: keyof SimFormatConfig, value: unknown) => {
    dispatch({
      type: 'UPDATE_CONFIG',
      configKey: `export.${formatId}`,
      value: { ...(cfg[formatId as keyof ExportConfig] as SimFormatConfig), [key]: value },
    });
  };

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '14px', fontFamily: 'var(--font-mono)', fontWeight: 900, color: '#e0e0ff', letterSpacing: '0.08em', margin: 0 }}>
          {PHASE_LABELS[phase]}
        </h2>
        <StatusBadge status={ps.status} />
      </div>

      <PhaseProgress progress={ps.progress} status={ps.status} label="SIM Export" estimatedTimeRemaining={ps.estimatedTimeRemaining} />

      <div style={{ fontSize: '10px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.1em', margin: '16px 0 10px', borderBottom: '1px solid rgba(255,255,255,0.04)', paddingBottom: '4px' }}>
        EXPORT TARGETS
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {SIM_FORMATS.map((fmt) => {
          const fCfg = cfg[fmt.id as keyof ExportConfig] as SimFormatConfig | undefined;
          if (!fCfg) return null;
          const enabled = fCfg.enabled;

          return (
            <div
              key={fmt.id}
              style={{
                padding: '12px',
                background: enabled ? 'rgba(0,240,255,0.03)' : 'rgba(255,255,255,0.01)',
                border: `1px solid ${enabled ? 'rgba(0,240,255,0.1)' : 'rgba(255,255,255,0.04)'}`,
                borderRadius: '4px',
                opacity: enabled ? 1 : 0.6,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button
                    onClick={() => !isLocked && updateFormat(fmt.id, 'enabled', !enabled)}
                    style={{
                      width: 14, height: 14, borderRadius: '2px',
                      background: enabled ? '#00f0ff' : 'transparent',
                      border: `1px solid ${enabled ? '#00f0ff' : '#444'}`,
                      cursor: isLocked ? 'not-allowed' : 'pointer',
                      padding: 0,
                    }}
                  />
                  <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: enabled ? '#e0e0ff' : '#666' }}>
                    {fmt.name}
                  </span>
                  <span style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)' }}>
                    {fmt.developer}
                  </span>
                </div>
              </div>

              {enabled && (
                <div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
                    {fmt.fileTypes.map(ft => (
                      <span
                        key={ft.extension}
                        title={ft.description}
                        style={{
                          padding: '2px 6px', fontSize: '9px',
                          fontFamily: 'var(--font-mono)',
                          background: 'rgba(255,255,255,0.04)',
                          border: '1px solid rgba(255,255,255,0.06)',
                          borderRadius: '2px', color: '#8888aa',
                        }}
                      >
                        {ft.extension}
                      </span>
                    ))}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                    <div>
                      <label style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)' }}>QUALITY</label>
                      <select
                        value={fCfg.textureQuality}
                        onChange={e => updateFormat(fmt.id, 'textureQuality', e.target.value)}
                        disabled={isLocked}
                        style={{
                          width: '100%', padding: '4px 6px', marginTop: '2px',
                          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.1)',
                          borderRadius: '3px', color: '#e0e0ff', fontSize: '10px', fontFamily: 'var(--font-mono)',
                        }}
                      >
                        {['low', 'medium', 'high', 'ultra'].map(q => (
                          <option key={q} value={q} style={{ background: '#1a1a2e' }}>{q.toUpperCase()}</option>
                        ))}
                      </select>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'end', paddingBottom: '2px' }}>
                      <ToggleMini label="AI" value={fCfg.includeAI} onChange={v => updateFormat(fmt.id, 'includeAI', v)} disabled={isLocked} />
                      <ToggleMini label="WX" value={fCfg.includeWeather} onChange={v => updateFormat(fmt.id, 'includeWeather', v)} disabled={isLocked} />
                    </div>
                  </div>

                  <div style={{ marginTop: '6px' }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      {fmt.features.map(f => (
                        <span key={f} style={{
                          padding: '1px 6px', fontSize: '8px',
                          fontFamily: 'var(--font-mono)',
                          color: '#555', borderRadius: '2px',
                          background: 'rgba(255,255,255,0.02)',
                        }}>
                          {f}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ToggleMini({ label, value, onChange, disabled }: { label: string; value: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      onClick={() => !disabled && onChange(!value)}
      style={{
        display: 'flex', alignItems: 'center', gap: '4px',
        padding: '4px 8px',
        background: value ? 'rgba(0,255,136,0.08)' : 'transparent',
        border: `1px solid ${value ? 'rgba(0,255,136,0.2)' : 'rgba(255,255,255,0.06)'}`,
        borderRadius: '2px',
        cursor: disabled ? 'not-allowed' : 'pointer',
      }}
    >
      <div style={{
        width: 8, height: 8, borderRadius: '1px',
        background: value ? '#00ff88' : 'transparent',
        border: `1px solid ${value ? '#00ff88' : '#444'}`,
      }} />
      <span style={{ fontSize: '9px', color: value ? '#00ff88' : '#555', fontFamily: 'var(--font-mono)' }}>{label}</span>
    </button>
  );
}
