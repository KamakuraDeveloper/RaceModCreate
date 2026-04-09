interface ParameterSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  tooltip?: string;
  onChange: (v: number) => void;
  disabled?: boolean;
}

export default function ParameterSlider({ label, value, min, max, step = 1, unit = '', tooltip, onChange, disabled }: ParameterSliderProps) {
  return (
    <div style={{ marginBottom: '10px' }} title={tooltip}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
        <label style={{ fontSize: '11px', color: '#8888aa', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em' }}>
          {label}
        </label>
        <span style={{ fontSize: '11px', color: '#00f0ff', fontFamily: 'var(--font-mono)' }}>
          {typeof value === 'number' ? (step < 1 ? value.toFixed(Math.max(1, -Math.floor(Math.log10(step)))) : value) : value}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={e => onChange(parseFloat(e.target.value))}
        style={{ width: '100%', accentColor: '#00f0ff', height: '4px', cursor: disabled ? 'not-allowed' : 'pointer' }}
      />
    </div>
  );
}
