import type {
  PipelineState,
  IngestConfig,
  SfMConfig,
  GaussianSplatConfig,
  MeshConfig,
  CourseConfig,
  ExportConfig,
  PhaseState,
  CourseInfo,
} from '../types/pipeline';
import { PipelinePhase, PhaseStatus, HDRMode, FeatureMatcherType, FeatureType, CameraModel, MeshMethod, UVMethod, SegmentationModel, SurfaceMaterial } from '../types/pipeline';

// APG Gotemba 752m Course defaults

export const DEFAULT_COURSE: CourseInfo = {
  name: 'APG Gotemba',
  length: 752,
  location: { lat: 35.3083, lng: 138.9350 },
  elevation: 468,
  turns: 8,
  country: 'Japan',
};

export const DEFAULT_INGEST: IngestConfig = {
  sourceFile: 'APG_Gotemba_360.insv',
  frameRate: 5,
  stabilization: true,
  hdrMode: HDRMode.ACES,
  gpsSync: true,
  imuSync: true,
  outputResolution: [5760, 2880],
  denoiseStrength: 0.3,
  exposureCompensation: 0.0,
  colorSpace: 'sRGB',
};

export const DEFAULT_SFM: SfMConfig = {
  matcher: FeatureMatcherType.SUPERGLUE,
  featureType: FeatureType.SUPERPOINT,
  cameraModel: CameraModel.EQUIRECTANGULAR,
  gpsGeoref: true,
  maxFeatures: 8192,
  matchRatio: 0.82,
  bundleAdjustment: true,
  robustTriangulation: true,
  minTrackLength: 3,
  filterMaxReprojError: 4.0,
};

export const DEFAULT_GAUSSIAN_SPLAT: GaussianSplatConfig = {
  iterations: 30000,
  learningRate: 0.0016,
  shDegree: 3,
  densifyInterval: 100,
  splitThreshold: 0.05,
  mipSplatting: true,
  antiAliasing: true,
  pruneThreshold: 0.005,
  positionLR: 0.00016,
  opacityLR: 0.05,
  scaleLR: 0.005,
  maxGaussians: 2000000,
};

export const DEFAULT_MESH: MeshConfig = {
  method: MeshMethod.SUGAR,
  textureResolution: 4096,
  generateNormalMap: true,
  generateAOMap: true,
  lodLevels: 3,
  uvMethod: UVMethod.XATLAS,
  decimationRatio: 0.5,
  smoothingIterations: 2,
  islandMargin: 4,
  maxTextureCount: 8,
};

export const DEFAULT_COURSE_CONFIG: CourseConfig = {
  segmentationModel: SegmentationModel.SAM2,
  roadDetectionThreshold: 0.85,
  surfaceMaterials: [
    SurfaceMaterial.ASPHALT,
    SurfaceMaterial.CURB,
    SurfaceMaterial.GRAVEL,
    SurfaceMaterial.GRASS,
  ],
  gripMap: true,
  racingLineDetection: true,
  trackWidth: 8.5,
  elevationSampling: 1.0,
  camberDetection: true,
  barrierDetection: true,
  pitLaneDetection: false,
};

export const DEFAULT_EXPORT: ExportConfig = {
  rfactor2: {
    enabled: true,
    outputPath: './export/rfactor2/',
    textureQuality: 'high',
    includeAI: true,
    includeWeather: true,
  },
  assettocorsa: {
    enabled: true,
    outputPath: './export/assettocorsa/',
    textureQuality: 'high',
    includeAI: true,
    includeWeather: false,
  },
  acc: {
    enabled: false,
    outputPath: './export/acc/',
    textureQuality: 'ultra',
    includeAI: true,
    includeWeather: true,
  },
  iracing: {
    enabled: false,
    outputPath: './export/iracing/',
    textureQuality: 'high',
    includeAI: true,
    includeWeather: false,
  },
  beamng: {
    enabled: false,
    outputPath: './export/beamng/',
    textureQuality: 'medium',
    includeAI: false,
    includeWeather: false,
  },
};

const defaultPhaseState = (): PhaseState => ({
  status: PhaseStatus.IDLE,
  progress: 0,
  startTime: null,
  duration: 0,
  metrics: { processingTime: 0, memoryUsage: 0 },
  estimatedTimeRemaining: null,
});

export const DEFAULT_PIPELINE_STATE: PipelineState = {
  phases: {
    [PipelinePhase.INGEST]: defaultPhaseState(),
    [PipelinePhase.SFM]: defaultPhaseState(),
    [PipelinePhase.GAUSSIAN_SPLAT]: defaultPhaseState(),
    [PipelinePhase.MESH]: defaultPhaseState(),
    [PipelinePhase.COURSE]: defaultPhaseState(),
    [PipelinePhase.EXPORT]: defaultPhaseState(),
  },
  configs: {
    ingest: DEFAULT_INGEST,
    sfm: DEFAULT_SFM,
    gaussianSplat: DEFAULT_GAUSSIAN_SPLAT,
    mesh: DEFAULT_MESH,
    course: DEFAULT_COURSE_CONFIG,
    export: DEFAULT_EXPORT,
  },
  course: DEFAULT_COURSE,
  activePhase: PipelinePhase.INGEST,
  logs: [],
  isRunning: false,
  startTime: null,
  totalElapsed: 0,
};
