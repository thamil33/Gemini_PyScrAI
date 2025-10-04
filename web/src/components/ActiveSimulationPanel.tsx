// Simplified active simulation control panel - focused on essential controls only
// Detailed views moved to SimulationDashboard

import { useSimulationStore } from '../stores/simulationStore';

export function ActiveSimulationPanel() {
  const { activeSimulation, isFetching, startSimulation, advanceSimulation } = 
    useSimulationStore();

  if (!activeSimulation) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <p className="text-gray-500 dark:text-gray-400 text-center">
          Select a simulation to view controls
        </p>
      </div>
    );
  }

  const canStart = activeSimulation.status === 'created';
  const canAdvance = activeSimulation.status === 'running';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
        {activeSimulation.name}
      </h2>
      
      <div className="space-y-4">
        {/* Quick Status Overview */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">Scenario:</span>
            <div className="font-medium text-gray-900 dark:text-white">{activeSimulation.scenario}</div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Status:</span>
            <div className="font-medium text-gray-900 dark:text-white">
              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                activeSimulation.status === 'running'
                  ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                  : activeSimulation.status === 'paused'
                  ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-400'
              }`}>
                {activeSimulation.status.toUpperCase()}
              </span>
            </div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Phase:</span>
            <div className="font-medium text-gray-900 dark:text-white">
              {activeSimulation.current_phase.replace(/_/g, ' ').toUpperCase()}
            </div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Cycle:</span>
            <div className="font-medium text-gray-900 dark:text-white">#{activeSimulation.phase_number}</div>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="pt-4 border-t border-gray-200 dark:border-gray-700 flex gap-3">
          {canStart && (
            <button
              onClick={() => startSimulation(activeSimulation.id)}
              disabled={isFetching}
              className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-md font-medium transition-colors"
            >
              {isFetching ? 'Starting...' : '▶️ Start Simulation'}
            </button>
          )}
          
          {canAdvance && (
            <button
              onClick={() => advanceSimulation(activeSimulation.id)}
              disabled={isFetching}
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-md font-medium transition-colors"
            >
              {isFetching ? 'Advancing...' : '⏭️ Advance Phase'}
            </button>
          )}
        </div>

        {/* Helpful note */}
        <div className="pt-2 text-xs text-gray-500 dark:text-gray-400 text-center">
          💡 View detailed simulation data in the dashboard below
        </div>
      </div>
    </div>
  );
}
