import type { ReactNode } from 'react';

interface TooltipProps {
  text: string;
  children: ReactNode;
}

export default function Tooltip({ text, children }: TooltipProps) {
  return (
    <span style={{ position: 'relative', display: 'inline-block' }} title={text}>
      {children}
    </span>
  );
}
