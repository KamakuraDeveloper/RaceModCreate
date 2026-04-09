interface ProgressRingProps {
  progress: number;     // 0-100
  size?: number;
  strokeWidth?: number;
  color?: string;
  bgColor?: string;
}

export default function ProgressRing({ progress, size = 48, strokeWidth = 3, color = '#00f0ff', bgColor = 'rgba(255,255,255,0.06)' }: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (progress / 100) * circumference;

  return (
    <div style={{ position: 'relative', width: size, height: size, flexShrink: 0 }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={bgColor} strokeWidth={strokeWidth} />
        <circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circumference} strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
      </svg>
      <span style={{
        position: 'absolute', inset: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: size < 40 ? '9px' : '11px',
        fontFamily: 'var(--font-mono)', fontWeight: 700,
        color: color,
        transform: 'rotate(0deg)',
      }}>
        {Math.round(progress)}%
      </span>
    </div>
  );
}
