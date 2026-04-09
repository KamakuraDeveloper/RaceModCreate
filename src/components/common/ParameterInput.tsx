interface ParameterInputProps {
  label: string;
  value: string | number;
  type?: 'text' | 'number';
  tooltip?: string;
  onChange: (v: string) => void;
  disabled?: boolean;
  unit?: string;
}

export default function ParameterInput({ label, value, type = 'text', tooltip, onChange, disabled, unit }: ParameterInputProps) {
  return (
    <div style={{ marginBottom: '10px' }} title={tooltip}>
      <label style={{ display: 'block', fontSize: '11px', color: '#8888aa', fontFamily: 'var(--font-mono)', letterSpacing: '0.05em', marginBottom: '4px' }}>
        {label}
      </label>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <input
          type={type}
          value={value}
          disabled={disabled}
          onChange={e => onChange(e.target.value)}
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.04)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '3px',
            padding: '6px 10px',
            color: '#e0e0ff',
            fontSize: '12px',
            fontFamily: 'var(--font-mono)',
            outline: 'none',
          }}
        />
        {unit && <span style={{ fontSize: '10px', color: '#666', fontFamily: 'var(--font-mono)' }}>{unit}</span>}
      </div>
    </div>
  );
}
