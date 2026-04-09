import { useRef, useEffect } from 'react';
import { usePipeline } from '../../hooks/usePipeline';
import { PHASE_SHORT, LogLevel } from '../../types/pipeline';

const LEVEL_COLOR: Record<string, string> = {
  INFO: '#8888aa',
  WARN: '#ffaa00',
  ERROR: '#ff003c',
  DEBUG: '#555',
  SUCCESS: '#00ff88',
};

export default function ConsoleOutput() {
  const { state } = usePipeline();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [state.logs.length]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', maxHeight: '200px' }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '6px 16px',
        background: 'rgba(0,0,0,0.3)',
        borderBottom: '1px solid rgba(255,255,255,0.04)',
        flexShrink: 0,
      }}>
        <span style={{ fontSize: '9px', color: '#555', fontFamily: 'var(--font-mono)', letterSpacing: '0.15em' }}>
          CONSOLE OUTPUT
        </span>
        <span style={{ fontSize: '9px', color: '#444', fontFamily: 'var(--font-mono)' }}>
          {state.logs.length} entries
        </span>
      </div>
      <div
        ref={containerRef}
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '8px 16px',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          lineHeight: '1.6',
        }}
      >
        {state.logs.length === 0 ? (
          <div style={{ color: '#333', fontStyle: 'italic' }}>Awaiting pipeline execution...</div>
        ) : (
          state.logs.map((log) => {
            const time = new Date(log.timestamp);
            const ts = `${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}:${time.getSeconds().toString().padStart(2, '0')}`;
            return (
              <div key={log.id} style={{ display: 'flex', gap: '8px', color: LEVEL_COLOR[log.level] ?? '#666' }}>
                <span style={{ color: '#333', flexShrink: 0 }}>{ts}</span>
                <span style={{
                  color: log.level === LogLevel.ERROR ? '#ff003c' : log.level === LogLevel.SUCCESS ? '#00ff88' : '#00f0ff',
                  flexShrink: 0, minWidth: '50px',
                }}>
                  [{PHASE_SHORT[log.phase]}]
                </span>
                <span style={{ color: LEVEL_COLOR[log.level] }}>{log.message}</span>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
