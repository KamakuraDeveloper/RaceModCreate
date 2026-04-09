// Sim format definitions for TRACK::FORGE export pipeline

export interface SimFormatDefinition {
  id: string;
  name: string;
  developer: string;
  fileTypes: { extension: string; description: string }[];
  description: string;
  features: string[];
}

export const SIM_FORMATS: SimFormatDefinition[] = [
  {
    id: 'rfactor2',
    name: 'rFactor 2',
    developer: 'Studio 397',
    fileTypes: [
      { extension: '.MAS', description: 'Packed asset archive' },
      { extension: '.TDF', description: 'Terrain definition file' },
      { extension: '.AIW', description: 'AI waypoint path file' },
      { extension: '.SCN', description: 'Scene definition file' },
      { extension: '.GDB', description: 'Track database file' },
    ],
    description: 'Professional-grade racing simulation with advanced tire and physics models.',
    features: ['Dynamic weather', 'AI racing line', 'Night lighting', 'Pit lane logic', 'Sector timing'],
  },
  {
    id: 'assettocorsa',
    name: 'Assetto Corsa',
    developer: 'Kunos Simulazioni',
    fileTypes: [
      { extension: '.KN5', description: '3D track model container' },
      { extension: 'surfaces.ini', description: 'Surface grip/material definition' },
      { extension: 'ai_line.fast', description: 'AI optimal racing line' },
      { extension: 'models.ini', description: 'Model configuration' },
    ],
    description: 'Highly moddable racing sim popular for track and car mods.',
    features: ['Custom shaders', 'Surface grip map', 'AI racing line', 'Camera paths', 'Dynamic track'],
  },
  {
    id: 'acc',
    name: 'Assetto Corsa Competizione',
    developer: 'Kunos Simulazioni',
    fileTypes: [
      { extension: '.KN5', description: '3D track model (UE4-enhanced)' },
      { extension: 'surfaces.ini', description: 'Surface definition' },
      { extension: 'ai_line.fast', description: 'AI racing line' },
      { extension: 'track.json', description: 'Track metadata config' },
      { extension: 'weather.json', description: 'Weather configuration' },
    ],
    description: 'GT3/GT4 focused sim with Unreal Engine 4 visuals.',
    features: ['UE4 rendering', 'Dynamic weather', 'Rubber buildup', 'Tire model v10', 'Broadcast HUD'],
  },
  {
    id: 'iracing',
    name: 'iRacing',
    developer: 'iRacing.com Motorsport Simulations',
    fileTypes: [
      { extension: '.W', description: 'iRacing world/track binary format' },
    ],
    description: 'Online competitive racing service with laser-scanned tracks.',
    features: ['Dynamic surfaces', 'Tire marbles', 'Night racing', 'Laser-scan accuracy', 'Multi-class'],
  },
  {
    id: 'beamng',
    name: 'BeamNG.drive',
    developer: 'BeamNG GmbH',
    fileTypes: [
      { extension: '.json', description: 'Terrain and world definition' },
      { extension: '.prefab', description: 'Prefab object placement' },
    ],
    description: 'Soft-body physics sandbox with realistic deformation.',
    features: ['Soft-body physics', 'Terrain deformation', 'Open world', 'Modular vehicles', 'Scenario editor'],
  },
];
