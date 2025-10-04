// Active simulation control panel

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
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">Scenario:</span>
            <div className="font-medium text-gray-900 dark:text-white">{activeSimulation.scenario}</div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Status:</span>
            <div className="font-medium text-gray-900 dark:text-white capitalize">{activeSimulation.status}</div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Current Phase:</span>
            <div className="font-medium text-gray-900 dark:text-white">
              {activeSimulation.current_phase.replace('_', ' ')}
            </div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Cycle Number:</span>
            <div className="font-medium text-gray-900 dark:text-white">{activeSimulation.phase_number}</div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Pending Actions:</span>
            <div className="font-medium text-gray-900 dark:text-white">{activeSimulation.pending_action_count}</div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">Pending Events:</span>
            <div className="font-medium text-gray-900 dark:text-white">{activeSimulation.pending_event_count}</div>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Known Actors</h3>
          {activeSimulation.actors.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">No actors have been registered yet.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {activeSimulation.actors.map((actor) => (
                <span
                  key={actor.id}
                  className="inline-flex items-center gap-2 rounded-full border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40 px-3 py-1 text-xs text-gray-700 dark:text-gray-200"
                >
                  <span className="font-medium text-gray-900 dark:text-white">{actor.name}</span>
                  <span className="uppercase tracking-wide text-gray-500 dark:text-gray-400">{actor.type}</span>
                </span>
              ))}
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Pending Actions</h3>
          {activeSimulation.pending_actions.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">No actions awaiting resolution.</p>
          ) : (
            <ul className="space-y-2">
              {activeSimulation.pending_actions.map((action) => (
                <li
                  key={action.id}
                  className="rounded-md border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/40 px-3 py-2"
                >
                  <div className="flex items-center justify-between text-sm">
                    <div className="font-medium text-gray-900 dark:text-white">
                      {action.intent}
                    </div>
                    <span className="text-xs uppercase tracking-wide text-blue-600 dark:text-blue-300">
                      {action.status}
                    </span>
                  </div>
                  <div className="mt-1 flex flex-wrap gap-x-3 text-xs text-gray-600 dark:text-gray-400">
                    <span>Actor: {action.actor_id}</span>
                    <span>Priority: {action.priority}</span>
                    <span>
                      Created:{' '}
                      {action.created_at
                        ? new Date(action.created_at).toLocaleString()
                        : '—'}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pt-4 border-t border-gray-200 dark:border-gray-700 flex gap-3">
          {canStart && (
            <button
              onClick={() => startSimulation(activeSimulation.id)}
              disabled={isFetching}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-md font-medium transition-colors"
            >
              {isFetching ? 'Starting...' : 'Start Simulation'}
            </button>
          )}
          
          {canAdvance && (
            <button
              onClick={() => advanceSimulation(activeSimulation.id)}
              disabled={isFetching}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-md font-medium transition-colors"
            >
              {isFetching ? 'Advancing...' : 'Advance Phase'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
