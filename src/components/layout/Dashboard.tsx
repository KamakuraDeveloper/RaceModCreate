import { PipelinePhase } from '../../types/pipeline';
import { usePipeline } from '../../hooks/usePipeline';
import PipelineOverview from '../pipeline/PipelineOverview';
import Phase1Ingest from '../phases/Phase1Ingest';
import Phase2SfM from '../phases/Phase2SfM';
import Phase3GaussianSplat from '../phases/Phase3GaussianSplat';
import Phase4Mesh from '../phases/Phase4Mesh';
import Phase5Course from '../phases/Phase5Course';
import Phase6Export from '../phases/Phase6Export';
import PipelineControls from '../controls/PipelineControls';
import ConsoleOutput from '../controls/ConsoleOutput';
import Preview3D from '../visualization/Preview3D';
import MetricsPanel from '../visualization/MetricsPanel';

const PHASE_COMPONENTS: Record<string, React.FC> = {
  INGEST: Phase1Ingest,
  SFM: Phase2SfM,
  GAUSSIAN_SPLAT: Phase3GaussianSplat,
  MESH: Phase4Mesh,
  COURSE: Phase5Course,
  EXPORT: Phase6Export,
};

export default function Dashboard() {
  const { state } = usePipeline();
  const ActivePhaseComponent = PHASE_COMPONENTS[state.activePhase] ?? Phase1Ingest;

  return (
    <div style={{
      flex: 1,
      display: 'grid',
      gridTemplateColumns: '1fr 340px',
      gridTemplateRows: 'auto 1fr auto',
      gap: '1px',
      background: 'rgba(255,255,255,0.02)',
      overflow: 'hidden',
    }}>
      {/* Pipeline overview - spans full width */}
      <div style={{ gridColumn: '1 / -1', background: '#0e0e16', padding: '12px 20px' }}>
        <PipelineOverview />
      </div>

      {/* Center: Active phase config + console */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: '#0c0c14',
      }}>
        <div style={{ flex: 1, overflow: 'auto', padding: '16px 20px' }}>
          <ActivePhaseComponent />
        </div>
        <div style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
          <PipelineControls phase={state.activePhase as PipelinePhase} />
        </div>
      </div>

      {/* Right: Preview + Metrics */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '1px',
        background: 'rgba(255,255,255,0.02)',
        overflow: 'hidden',
      }}>
        <Preview3D />
        <MetricsPanel />
      </div>

      {/* Console - spans full width */}
      <div style={{ gridColumn: '1 / -1', background: '#0a0a10', maxHeight: '200px' }}>
        <ConsoleOutput />
      </div>
    </div>
  );
}
