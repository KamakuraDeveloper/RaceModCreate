import { useEffect } from 'react';
import { usePipeline } from './hooks/usePipeline';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './components/layout/Dashboard';

export default function App() {
  const { dispatch, state } = usePipeline();

  // Tick elapsed time
  useEffect(() => {
    if (!state.isRunning) return;
    const id = setInterval(() => dispatch({ type: 'TICK_ELAPSED' }), 1000);
    return () => clearInterval(id);
  }, [state.isRunning, dispatch]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden', background: '#0a0a0f', color: '#e0e0ff' }}>
      <Header />
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <Sidebar />
        <Dashboard />
      </div>
    </div>
  );
}
