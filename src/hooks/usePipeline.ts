import { useContext, useRef, useCallback, useEffect } from 'react';
import { PipelineContext } from '../store/PipelineContext';
import type { PipelinePhase, PhaseMetrics } from '../types/pipeline';
import { PhaseStatus, LogLevel, PHASE_ORDER } from '../types/pipeline';

// Simulated log messages per phase
const SIM_LOGS: Record<string, string[]> = {
  INGEST: [
    'Loading Insta360 .insv container...',
    'Parsing dual-lens fisheye streams...',
    'Applying FlowState gyro stabilization...',
    'Stitching equirectangular frames...',
    'Tone mapping HDR (ACES filmic)...',
    'Syncing GPS/IMU telemetry overlay...',
    'Extracting adaptive keyframes @ 5fps...',
    'Writing frame buffer to staging...',
    'Frame quality validation pass...',
    'Ingest pipeline complete.',
  ],
  SFM: [
    'Initializing COLMAP workspace...',
    'Running SuperPoint feature extraction...',
    'Detecting 8192 features per frame...',
    'SuperGlue matching pairs (sequential)...',
    'Building feature graph adjacency...',
    'Incremental mapper — registering images...',
    'Bundle adjustment iteration 1/3...',
    'Bundle adjustment iteration 2/3...',
    'Bundle adjustment iteration 3/3...',
    'GPS georeferencing alignment...',
    'Triangulating sparse point cloud...',
    'Filtering points (reproj error < 4.0px)...',
    'SfM reconstruction complete.',
  ],
  GAUSSIAN_SPLAT: [
    'Initializing 3D Gaussian primitives from SfM...',
    'Setting SH degree=3, densify interval=100...',
    'Training iteration 1000/30000 | Loss: 0.0842...',
    'Training iteration 5000/30000 | Loss: 0.0421...',
    'Densification: split 12,431 Gaussians...',
    'Training iteration 10000/30000 | Loss: 0.0284...',
    'Pruning low-opacity Gaussians (τ=0.005)...',
    'Training iteration 20000/30000 | Loss: 0.0163...',
    'Mip-Splatting anti-aliasing enabled...',
    'Training iteration 30000/30000 | Loss: 0.0098...',
    'Gaussian count: 1,847,293...',
    '3DGS training converged.',
  ],
  MESH: [
    'Initializing SuGaR surface extraction...',
    'Computing level-set from Gaussian density...',
    'Marching cubes @ resolution 512³...',
    'Raw mesh: 2,847,102 faces...',
    'Decimating to target ratio 0.5...',
    'Laplacian smoothing (2 iterations)...',
    'UV unwrap via xatlas...',
    'Baking diffuse texture atlas (4096×4096)...',
    'Generating normal map...',
    'Generating ambient occlusion map...',
    'Building LOD chain (3 levels)...',
    'Mesh conversion complete.',
  ],
  COURSE: [
    'Loading SAM2 segmentation model...',
    'Running road surface detection...',
    'Threshold: 0.85 confidence...',
    'Classifying surface materials...',
    'Detected: asphalt (94%), curb (3%), gravel (2%), grass (1%)...',
    'Computing grip coefficient map...',
    'Detecting GPS trajectory racing line...',
    'Sampling elevation profile @ 1m intervals...',
    'Detecting camber angles...',
    'Barrier detection pass...',
    'Track width: 8.5m average...',
    'Course construction complete.',
  ],
  EXPORT: [
    'Preparing rFactor 2 export...',
    'Generating .MAS asset archive...',
    'Writing .TDF terrain definition...',
    'Computing .AIW waypoint path...',
    'Preparing Assetto Corsa export...',
    'Packing .KN5 model container...',
    'Writing surfaces.ini grip map...',
    'Generating ai_line.fast racing line...',
    'Export complete: 2 formats generated.',
  ],
};

const PHASE_DURATIONS: Record<string, number> = {
  INGEST: 8000,
  SFM: 12000,
  GAUSSIAN_SPLAT: 15000,
  MESH: 10000,
  COURSE: 8000,
  EXPORT: 6000,
};

const PHASE_FINAL_METRICS: Record<string, PhaseMetrics> = {
  INGEST: { processingTime: 8, memoryUsage: 2048, framesExtracted: 376 },
  SFM: { processingTime: 12, memoryUsage: 4096, pointCloudDensity: 284731, featuresMatched: 1247892 },
  GAUSSIAN_SPLAT: { processingTime: 15, memoryUsage: 8192, gaussianCount: 1847293 },
  MESH: { processingTime: 10, memoryUsage: 6144, meshFaces: 1423551, textureResolution: '4096×4096' },
  COURSE: { processingTime: 8, memoryUsage: 3072, surfaceArea: 6392, trackLength: 752 },
  EXPORT: { processingTime: 6, memoryUsage: 2048, exportedFormats: 2 },
};

export function usePipeline() {
  const context = useContext(PipelineContext);
  if (!context) throw new Error('usePipeline must be used within PipelineProvider');

  const { state, startPhase, pausePhase, resumePhase, completePhase, updateProgress, addLog, setActivePhase, resetPipeline } = context;
  const timerRefs = useRef<Map<string, number>>(new Map());

  const stopSimulation = useCallback((phase: PipelinePhase) => {
    const id = timerRefs.current.get(phase);
    if (id !== undefined) {
      clearInterval(id);
      timerRefs.current.delete(phase);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    const refs = timerRefs.current;
    return () => {
      refs.forEach((id) => clearInterval(id));
      refs.clear();
    };
  }, []);

  const simulatePhase = useCallback((phase: PipelinePhase) => {
    stopSimulation(phase);
    startPhase(phase);
    setActivePhase(phase);
    addLog(phase, LogLevel.INFO, `Phase ${phase} started`);

    const logs = SIM_LOGS[phase] ?? [];
    const duration = PHASE_DURATIONS[phase] ?? 10000;
    const interval = 200;
    const totalTicks = duration / interval;
    let tick = 0;
    let logIndex = 0;
    const logInterval = Math.max(1, Math.floor(totalTicks / logs.length));

    const timerId = window.setInterval(() => {
      tick++;
      const progress = Math.min(100, (tick / totalTicks) * 100);

      // Simulate metrics evolving
      const finalMetrics = PHASE_FINAL_METRICS[phase] ?? { processingTime: 0, memoryUsage: 0 };
      const fraction = progress / 100;
      const currentMetrics: Partial<PhaseMetrics> = {
        processingTime: +(finalMetrics.processingTime * fraction).toFixed(1),
        memoryUsage: Math.round(finalMetrics.memoryUsage * Math.min(1, fraction + 0.2)),
      };
      if (finalMetrics.framesExtracted) currentMetrics.framesExtracted = Math.round(finalMetrics.framesExtracted * fraction);
      if (finalMetrics.pointCloudDensity) currentMetrics.pointCloudDensity = Math.round(finalMetrics.pointCloudDensity * fraction);
      if (finalMetrics.featuresMatched) currentMetrics.featuresMatched = Math.round(finalMetrics.featuresMatched * fraction);
      if (finalMetrics.gaussianCount) currentMetrics.gaussianCount = Math.round(finalMetrics.gaussianCount * fraction);
      if (finalMetrics.meshFaces) currentMetrics.meshFaces = Math.round(finalMetrics.meshFaces * fraction);
      if (finalMetrics.surfaceArea) currentMetrics.surfaceArea = Math.round(finalMetrics.surfaceArea * fraction);

      const etr = Math.max(0, ((totalTicks - tick) * interval) / 1000);
      updateProgress(phase, progress, currentMetrics, etr);

      // Emit log messages
      if (tick % logInterval === 0 && logIndex < logs.length) {
        addLog(phase, LogLevel.INFO, logs[logIndex]);
        logIndex++;
      }

      if (tick >= totalTicks) {
        stopSimulation(phase);
        completePhase(phase, PHASE_FINAL_METRICS[phase] ?? { processingTime: 0, memoryUsage: 0 });
        addLog(phase, LogLevel.SUCCESS, `Phase ${phase} completed successfully`);
      }
    }, interval);

    timerRefs.current.set(phase, timerId);
  }, [startPhase, setActivePhase, addLog, updateProgress, completePhase, stopSimulation]);

  const runPhase = useCallback((phase: PipelinePhase) => {
    const phaseState = state.phases[phase];
    if (phaseState.status === PhaseStatus.RUNNING) return;
    if (phaseState.status === PhaseStatus.PAUSED) {
      resumePhase(phase);
      return;
    }
    simulatePhase(phase);
  }, [state.phases, simulatePhase, resumePhase]);

  const pauseCurrentPhase = useCallback((phase: PipelinePhase) => {
    stopSimulation(phase);
    pausePhase(phase);
    addLog(phase, LogLevel.WARN, `Phase ${phase} paused`);
  }, [stopSimulation, pausePhase, addLog]);

  const runAll = useCallback(() => {
    let delay = 0;
    for (const phase of PHASE_ORDER) {
      if (state.phases[phase].status === PhaseStatus.COMPLETED) continue;
      const d = delay;
      setTimeout(() => simulatePhase(phase), d);
      delay += (PHASE_DURATIONS[phase] ?? 10000) + 500;
    }
  }, [state.phases, simulatePhase]);

  const stopAll = useCallback(() => {
    for (const phase of PHASE_ORDER) {
      stopSimulation(phase);
    }
  }, [stopSimulation]);

  return {
    state,
    runPhase,
    pauseCurrentPhase,
    runAll,
    stopAll,
    setActivePhase,
    resetPipeline,
    addLog,
    dispatch: context.dispatch,
  };
}
