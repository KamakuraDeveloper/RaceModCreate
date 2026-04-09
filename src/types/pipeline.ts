// Pipeline Phase identifiers
export const PipelinePhase = {
  INGEST: 'INGEST',
  SFM: 'SFM',
  GAUSSIAN_SPLAT: 'GAUSSIAN_SPLAT',
  MESH: 'MESH',
  COURSE: 'COURSE',
  EXPORT: 'EXPORT',
} as const;
export type PipelinePhase = (typeof PipelinePhase)[keyof typeof PipelinePhase];

export const PHASE_ORDER: PipelinePhase[] = [
  PipelinePhase.INGEST,
  PipelinePhase.SFM,
  PipelinePhase.GAUSSIAN_SPLAT,
  PipelinePhase.MESH,
  PipelinePhase.COURSE,
  PipelinePhase.EXPORT,
];

export const PHASE_LABELS: Record<PipelinePhase, string> = {
  INGEST: '01 › VIDEO INGEST',
  SFM: '02 › SfM RECONSTRUCT',
  GAUSSIAN_SPLAT: '03 › 3D GAUSSIAN SPLAT',
  MESH: '04 › MESH CONVERT',
  COURSE: '05 › COURSE BUILD',
  EXPORT: '06 › SIM EXPORT',
};

export const PHASE_SHORT: Record<PipelinePhase, string> = {
  INGEST: 'INGEST',
  SFM: 'SfM',
  GAUSSIAN_SPLAT: '3DGS',
  MESH: 'MESH',
  COURSE: 'COURSE',
  EXPORT: 'EXPORT',
};

// Phase status
export const PhaseStatus = {
  IDLE: 'IDLE',
  QUEUED: 'QUEUED',
  RUNNING: 'RUNNING',
  PAUSED: 'PAUSED',
  COMPLETED: 'COMPLETED',
  ERROR: 'ERROR',
} as const;
export type PhaseStatus = (typeof PhaseStatus)[keyof typeof PhaseStatus];

// HDR mode
export const HDRMode = {
  NONE: 'none',
  REINHARD: 'reinhard',
  ACES: 'aces',
  FILMIC: 'filmic',
} as const;
export type HDRMode = (typeof HDRMode)[keyof typeof HDRMode];

// Feature matcher type
export const FeatureMatcherType = {
  SUPERGLUE: 'superglue',
  NEAREST_NEIGHBOR: 'nearest_neighbor',
  FLANN: 'flann',
} as const;
export type FeatureMatcherType = (typeof FeatureMatcherType)[keyof typeof FeatureMatcherType];

// Feature type
export const FeatureType = {
  SUPERPOINT: 'superpoint',
  SIFT: 'sift',
  ORB: 'orb',
} as const;
export type FeatureType = (typeof FeatureType)[keyof typeof FeatureType];

// Camera model
export const CameraModel = {
  EQUIRECTANGULAR: 'equirectangular',
  FISHEYE: 'fisheye',
  PINHOLE: 'pinhole',
} as const;
export type CameraModel = (typeof CameraModel)[keyof typeof CameraModel];

// Mesh extraction method
export const MeshMethod = {
  SUGAR: 'sugar',
  TWO_DGS: '2dgs',
  POISSON: 'poisson',
} as const;
export type MeshMethod = (typeof MeshMethod)[keyof typeof MeshMethod];

// UV unwrap method
export const UVMethod = {
  XATLAS: 'xatlas',
  SMART_UV: 'smart_uv',
  LIGHTMAP: 'lightmap',
} as const;
export type UVMethod = (typeof UVMethod)[keyof typeof UVMethod];

// Segmentation model
export const SegmentationModel = {
  SAM2: 'sam2',
  MASK_RCNN: 'mask_rcnn',
  DEEPLABV3: 'deeplabv3',
} as const;
export type SegmentationModel = (typeof SegmentationModel)[keyof typeof SegmentationModel];

// Surface material types
export const SurfaceMaterial = {
  ASPHALT: 'asphalt',
  CONCRETE: 'concrete',
  CURB: 'curb',
  GRAVEL: 'gravel',
  GRASS: 'grass',
  SAND: 'sand',
  RUMBLE_STRIP: 'rumble_strip',
} as const;
export type SurfaceMaterial = (typeof SurfaceMaterial)[keyof typeof SurfaceMaterial];

// Log level
export const LogLevel = {
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
  DEBUG: 'DEBUG',
  SUCCESS: 'SUCCESS',
} as const;
export type LogLevel = (typeof LogLevel)[keyof typeof LogLevel];

// --- Configuration interfaces ---

export interface IngestConfig {
  sourceFile: string;
  frameRate: number;          // 1-10 fps adaptive extraction
  stabilization: boolean;     // FlowState stabilization
  hdrMode: HDRMode;
  gpsSync: boolean;
  imuSync: boolean;
  outputResolution: [number, number]; // width, height
  denoiseStrength: number;    // 0-1
  exposureCompensation: number; // -3 to +3 EV
  colorSpace: string;
}

export interface SfMConfig {
  matcher: FeatureMatcherType;
  featureType: FeatureType;
  cameraModel: CameraModel;
  gpsGeoref: boolean;
  maxFeatures: number;        // per image
  matchRatio: number;         // 0-1
  bundleAdjustment: boolean;
  robustTriangulation: boolean;
  minTrackLength: number;
  filterMaxReprojError: number;
}

export interface GaussianSplatConfig {
  iterations: number;
  learningRate: number;
  shDegree: number;           // 0-4
  densifyInterval: number;
  splitThreshold: number;
  mipSplatting: boolean;
  antiAliasing: boolean;
  pruneThreshold: number;
  positionLR: number;
  opacityLR: number;
  scaleLR: number;
  maxGaussians: number;
}

export interface MeshConfig {
  method: MeshMethod;
  textureResolution: number;  // 4096 or 8192
  generateNormalMap: boolean;
  generateAOMap: boolean;
  lodLevels: number;          // 1-5
  uvMethod: UVMethod;
  decimationRatio: number;    // 0-1
  smoothingIterations: number;
  islandMargin: number;
  maxTextureCount: number;
}

export interface CourseConfig {
  segmentationModel: SegmentationModel;
  roadDetectionThreshold: number; // 0-1
  surfaceMaterials: SurfaceMaterial[];
  gripMap: boolean;
  racingLineDetection: boolean;
  trackWidth: number;         // meters
  elevationSampling: number;  // meters interval
  camberDetection: boolean;
  barrierDetection: boolean;
  pitLaneDetection: boolean;
}

export interface SimFormatConfig {
  enabled: boolean;
  outputPath: string;
  textureQuality: 'low' | 'medium' | 'high' | 'ultra';
  includeAI: boolean;
  includeWeather: boolean;
}

export interface ExportConfig {
  rfactor2: SimFormatConfig;
  assettocorsa: SimFormatConfig;
  acc: SimFormatConfig;
  iracing: SimFormatConfig;
  beamng: SimFormatConfig;
}

// --- Log entry ---

export interface LogEntry {
  id: string;
  timestamp: number;
  phase: PipelinePhase;
  level: LogLevel;
  message: string;
}

// --- Phase state ---

export interface PhaseMetrics {
  processingTime: number;       // seconds
  memoryUsage: number;          // MB
  pointCloudDensity?: number;
  gaussianCount?: number;
  meshFaces?: number;
  textureResolution?: string;
  framesExtracted?: number;
  featuresMatched?: number;
  surfaceArea?: number;
  trackLength?: number;
  exportedFormats?: number;
}

export interface PhaseState {
  status: PhaseStatus;
  progress: number;             // 0-100
  startTime: number | null;
  duration: number;             // seconds
  metrics: PhaseMetrics;
  estimatedTimeRemaining: number | null;
}

// --- Global pipeline state ---

export interface CourseInfo {
  name: string;
  length: number;               // meters
  location: { lat: number; lng: number };
  elevation: number;            // meters
  turns: number;
  country: string;
}

export interface PipelineState {
  phases: Record<PipelinePhase, PhaseState>;
  configs: {
    ingest: IngestConfig;
    sfm: SfMConfig;
    gaussianSplat: GaussianSplatConfig;
    mesh: MeshConfig;
    course: CourseConfig;
    export: ExportConfig;
  };
  course: CourseInfo;
  activePhase: PipelinePhase;
  logs: LogEntry[];
  isRunning: boolean;
  startTime: number | null;
  totalElapsed: number;
}

// --- Actions ---

export type PipelineAction =
  | { type: 'START_PHASE'; phase: PipelinePhase }
  | { type: 'PAUSE_PHASE'; phase: PipelinePhase }
  | { type: 'RESUME_PHASE'; phase: PipelinePhase }
  | { type: 'COMPLETE_PHASE'; phase: PipelinePhase; metrics: PhaseMetrics }
  | { type: 'ERROR_PHASE'; phase: PipelinePhase; error: string }
  | { type: 'UPDATE_PROGRESS'; phase: PipelinePhase; progress: number; metrics?: Partial<PhaseMetrics>; estimatedTimeRemaining?: number }
  | { type: 'UPDATE_CONFIG'; configKey: string; value: unknown }
  | { type: 'ADD_LOG'; entry: LogEntry }
  | { type: 'SET_ACTIVE_PHASE'; phase: PipelinePhase }
  | { type: 'RESET_PIPELINE' }
  | { type: 'TICK_ELAPSED' };
