import { createContext } from 'react';
import type {
  PipelineState,
  PipelineAction,
  PipelinePhase,
  PhaseMetrics,
  LogLevel,
} from '../types/pipeline';

export interface PipelineContextValue {
  state: PipelineState;
  dispatch: React.Dispatch<PipelineAction>;
  startPhase: (phase: PipelinePhase) => void;
  pausePhase: (phase: PipelinePhase) => void;
  resumePhase: (phase: PipelinePhase) => void;
  completePhase: (phase: PipelinePhase, metrics: PhaseMetrics) => void;
  errorPhase: (phase: PipelinePhase, error: string) => void;
  updateProgress: (phase: PipelinePhase, progress: number, metrics?: Partial<PhaseMetrics>, etr?: number) => void;
  addLog: (phase: PipelinePhase, level: LogLevel, message: string) => void;
  setActivePhase: (phase: PipelinePhase) => void;
  resetPipeline: () => void;
}

export const PipelineContext = createContext<PipelineContextValue | null>(null);
