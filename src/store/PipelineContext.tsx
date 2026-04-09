import { useReducer, useCallback, type ReactNode } from 'react';
import type {
  PipelineState,
  PipelineAction,
  PipelinePhase,
  PhaseMetrics,
  LogEntry,
  LogLevel,
} from '../types/pipeline';
import { PhaseStatus } from '../types/pipeline';
import { DEFAULT_PIPELINE_STATE } from '../config/defaults';
import { PipelineContext } from './pipelineContext';
import type { PipelineContextValue } from './pipelineContext';

function pipelineReducer(state: PipelineState, action: PipelineAction): PipelineState {
  switch (action.type) {
    case 'START_PHASE': {
      const now = Date.now();
      return {
        ...state,
        isRunning: true,
        startTime: state.startTime ?? now,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            status: PhaseStatus.RUNNING,
            progress: 0,
            startTime: now,
            duration: 0,
            estimatedTimeRemaining: null,
          },
        },
      };
    }
    case 'PAUSE_PHASE':
      return {
        ...state,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            status: PhaseStatus.PAUSED,
          },
        },
      };
    case 'RESUME_PHASE':
      return {
        ...state,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            status: PhaseStatus.RUNNING,
          },
        },
      };
    case 'COMPLETE_PHASE':
      return {
        ...state,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            status: PhaseStatus.COMPLETED,
            progress: 100,
            metrics: action.metrics,
            estimatedTimeRemaining: 0,
            duration: state.phases[action.phase].startTime
              ? (Date.now() - state.phases[action.phase].startTime!) / 1000
              : 0,
          },
        },
      };
    case 'ERROR_PHASE':
      return {
        ...state,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            status: PhaseStatus.ERROR,
          },
        },
      };
    case 'UPDATE_PROGRESS':
      return {
        ...state,
        phases: {
          ...state.phases,
          [action.phase]: {
            ...state.phases[action.phase],
            progress: action.progress,
            metrics: {
              ...state.phases[action.phase].metrics,
              ...(action.metrics ?? {}),
            },
            estimatedTimeRemaining: action.estimatedTimeRemaining ?? state.phases[action.phase].estimatedTimeRemaining,
            duration: state.phases[action.phase].startTime
              ? (Date.now() - state.phases[action.phase].startTime!) / 1000
              : 0,
          },
        },
      };
    case 'UPDATE_CONFIG': {
      const keys = action.configKey.split('.');
      if (keys.length === 2) {
        const [section, key] = keys;
        const sectionKey = section as keyof PipelineState['configs'];
        return {
          ...state,
          configs: {
            ...state.configs,
            [sectionKey]: {
              ...(state.configs[sectionKey] as unknown as Record<string, unknown>),
              [key]: action.value,
            },
          },
        };
      }
      return state;
    }
    case 'ADD_LOG':
      return {
        ...state,
        logs: [...state.logs, action.entry],
      };
    case 'SET_ACTIVE_PHASE':
      return { ...state, activePhase: action.phase };
    case 'RESET_PIPELINE':
      return { ...DEFAULT_PIPELINE_STATE, logs: [] };
    case 'TICK_ELAPSED':
      return {
        ...state,
        totalElapsed: state.startTime ? (Date.now() - state.startTime) / 1000 : 0,
      };
    default:
      return state;
  }
}

export { PipelineContext } from './pipelineContext';
export type { PipelineContextValue } from './pipelineContext';

export function PipelineProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(pipelineReducer, DEFAULT_PIPELINE_STATE);

  const startPhase = useCallback((phase: PipelinePhase) => {
    dispatch({ type: 'START_PHASE', phase });
  }, []);

  const pausePhase = useCallback((phase: PipelinePhase) => {
    dispatch({ type: 'PAUSE_PHASE', phase });
  }, []);

  const resumePhase = useCallback((phase: PipelinePhase) => {
    dispatch({ type: 'RESUME_PHASE', phase });
  }, []);

  const completePhase = useCallback((phase: PipelinePhase, metrics: PhaseMetrics) => {
    dispatch({ type: 'COMPLETE_PHASE', phase, metrics });
  }, []);

  const errorPhase = useCallback((phase: PipelinePhase, error: string) => {
    dispatch({ type: 'ERROR_PHASE', phase, error });
  }, []);

  const updateProgress = useCallback((phase: PipelinePhase, progress: number, metrics?: Partial<PhaseMetrics>, estimatedTimeRemaining?: number) => {
    dispatch({ type: 'UPDATE_PROGRESS', phase, progress, metrics, estimatedTimeRemaining });
  }, []);

  const addLog = useCallback((phase: PipelinePhase, level: LogLevel, message: string) => {
    const entry: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      timestamp: Date.now(),
      phase,
      level,
      message,
    };
    dispatch({ type: 'ADD_LOG', entry });
  }, []);

  const setActivePhase = useCallback((phase: PipelinePhase) => {
    dispatch({ type: 'SET_ACTIVE_PHASE', phase });
  }, []);

  const resetPipeline = useCallback(() => {
    dispatch({ type: 'RESET_PIPELINE' });
  }, []);

  const value: PipelineContextValue = {
    state,
    dispatch,
    startPhase,
    pausePhase,
    resumePhase,
    completePhase,
    errorPhase,
    updateProgress,
    addLog,
    setActivePhase,
    resetPipeline,
  };

  return (
    <PipelineContext value={value}>
      {children}
    </PipelineContext>
  );
}
