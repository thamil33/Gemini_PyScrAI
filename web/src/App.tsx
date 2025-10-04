import { useEffect } from 'react';
import { DashboardLayout } from './components/DashboardLayout';
import { SimulationList } from './components/SimulationList';
import { CreateSimulationForm } from './components/CreateSimulationForm';
import { SimulationDashboard } from './components/SimulationDashboard';
import { ToastContainer } from './components/ToastContainer';
import { useSimulationStore } from './stores/simulationStore';

function App() {
  const { error, clearError, startPolling, stopPolling, disconnectStream, activeSimulation } = useSimulationStore();

  useEffect(() => {
    // Start polling when component mounts
    startPolling();
    
    // Cleanup on unmount
    return () => {
      disconnectStream();
      stopPolling();
    };
  }, [startPolling, stopPolling, disconnectStream]);

  return (
    <DashboardLayout>
      <ToastContainer />
      {error && (
        <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <p className="text-red-800 dark:text-red-200">{error}</p>
            <button
              onClick={clearError}
              className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {!activeSimulation ? (
        // Simulation Selection View
        <div className="space-y-6">
          <div className="mb-6">
            <CreateSimulationForm />
          </div>

          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Your Simulations
            </h2>
            <SimulationList showRemoveButton={true} />
          </div>
        </div>
      ) : (
        // Full Dashboard View (when simulation is active)
        <SimulationDashboard simulation={activeSimulation} />
      )}
    </DashboardLayout>
  );
}

export default App;
