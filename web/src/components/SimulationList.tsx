// Simulation list component

import { useEffect } from 'react';
import { useSimulationStore } from '../stores/simulationStore';

interface SimulationListProps {
  showRemoveButton?: boolean;
}

export function SimulationList({ showRemoveButton = false }: SimulationListProps = {}) {
  const { simulations, activeSimulation, isFetching, fetchSimulations, selectSimulation, deleteSimulation } =
    useSimulationStore();

  useEffect(() => {
    fetchSimulations();
  }, [fetchSimulations]);

  const handleDeleteSimulation = async (simulationId: string) => {
    try {
      await deleteSimulation(simulationId);
      await fetchSimulations(); // Refresh the list after deletion
    } catch (error) {
      console.error('Failed to delete simulation:', error);
    }
  };

  const getPhaseColor = (phase: string) => {
    const colors: Record<string, string> = {
      initialize: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      event_generation: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      action_collection: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      action_resolution: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      world_update: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      snapshot: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-200',
    };
    return colors[phase] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      created: 'bg-gray-100 text-gray-800',
      running: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-blue-100 text-blue-800',
      error: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (isFetching && simulations.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
        <p className="mt-2 text-gray-600 dark:text-gray-400">Loading simulations...</p>
      </div>
    );
  }

  if (simulations.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        No simulations found. Create one to get started.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {simulations.map((sim) => (
        <div
          key={sim.id}
          className={`
            bg-white dark:bg-gray-800 rounded-lg shadow-sm border p-4
            transition-all hover:shadow-md
            ${activeSimulation?.id === sim.id
              ? 'border-blue-500 ring-2 ring-blue-200 dark:ring-blue-800'
              : 'border-gray-200 dark:border-gray-700'}
          `}
        >
          <div className="flex items-center justify-between">
            <div
              className="flex-1 cursor-pointer"
              onClick={() => selectSimulation(sim.id)}
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                {sim.name}
              </h3>
              <div className="mt-2 flex items-center gap-2 flex-wrap">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(sim.status)}`}>
                  {sim.status}
                </span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPhaseColor(sim.current_phase)}`}>
                  {sim.current_phase.replace('_', ' ')}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Cycle #{sim.phase_number}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right text-sm text-gray-500 dark:text-gray-400">
                <div>Actions: {sim.pending_action_count}</div>
                <div>Events: {sim.pending_event_count}</div>
              </div>
              {showRemoveButton && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Are you sure you want to delete the simulation "${sim.name}"?`)) {
                      handleDeleteSimulation(sim.id);
                    }
                  }}
                  className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                  title="Delete simulation"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
