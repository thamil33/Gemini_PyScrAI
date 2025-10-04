// Comprehensive simulation dashboard with researcher mediation UI

import { useState } from 'react';
import { SimulationDetail } from '../types/api';
import { EventViewer } from './EventViewer';
import { ActionViewer } from './ActionViewer';
import { PhaseLogViewer } from './PhaseLogViewer';
import { ActorManager } from './ActorManager';
import { ActionComposer } from './ActionComposer';
import { useSimulationStore } from '../stores/simulationStore';

interface SimulationDashboardProps {
  simulation: SimulationDetail;
}

type ViewMode = 'workspace' | 'map' | 'data';

export function SimulationDashboard({ simulation }: SimulationDashboardProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('workspace');
  const { isFetching, startSimulation, advanceSimulation, selectSimulation } = useSimulationStore();

  const canStart = simulation.status === 'created';
  const canAdvance = simulation.status === 'running';

  return (
    <div className="space-y-4">
      {/* Top Control Bar */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-4">
            <button
              onClick={() => selectSimulation('')}
              className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              title="Back to simulation list"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                {simulation.name}
              </h1>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {simulation.scenario} • {simulation.status.toUpperCase()}
              </p>
            </div>
          </div>

          {/* View Mode Switcher */}
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('workspace')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                viewMode === 'workspace'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              🎛️ Workspace
            </button>
            <button
              onClick={() => setViewMode('map')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                viewMode === 'map'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
              title="Map view (coming soon)"
            >
              🗺️ Map
            </button>
            <button
              onClick={() => setViewMode('data')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                viewMode === 'data'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
              }`}
            >
              📊 Data
            </button>
          </div>
        </div>

        {/* Phase Controls & Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {/* Current Phase Card */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">
              Current Phase
            </div>
            <div className="text-lg font-bold text-blue-900 dark:text-blue-100">
              {simulation.current_phase.replace(/_/g, ' ').toUpperCase()}
            </div>
            <div className="text-xs text-blue-700 dark:text-blue-300">
              Cycle #{simulation.phase_number}
            </div>
          </div>

          {/* Quick Metrics */}
          <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Actors</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {simulation.actors?.length || 0}
            </div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Events</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {simulation.pending_event_count || 0}
            </div>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Actions</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {simulation.pending_action_count || 0}
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex flex-col gap-2">
            {canStart && (
              <button
                onClick={() => startSimulation(simulation.id)}
                disabled={isFetching}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-medium text-sm transition-colors"
              >
                {isFetching ? '...' : '▶️ Start'}
              </button>
            )}
            {canAdvance && (
              <button
                onClick={() => advanceSimulation(simulation.id)}
                disabled={isFetching}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-medium text-sm transition-colors"
              >
                {isFetching ? '...' : '⏭️ Advance'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      {viewMode === 'workspace' && <WorkspaceView simulation={simulation} />}
      {viewMode === 'map' && <MapView simulation={simulation} />}
      {viewMode === 'data' && <DataView simulation={simulation} />}
    </div>
  );
}

// Workspace View: Researcher mediation interface
function WorkspaceView({ simulation }: { simulation: SimulationDetail }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Left Column: Events & Actions Mediation */}
      <div className="lg:col-span-2 space-y-4">
        {/* Event Review Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                🔍 Event Review & Mediation
              </h2>
              <span className="px-2 py-1 text-xs rounded-full bg-purple-100 dark:bg-purple-900/20 text-purple-800 dark:text-purple-400">
                {simulation.pending_events?.length || 0} pending
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              Review LLM-generated events before they affect the simulation. Edit descriptions and effects as needed.
            </p>
          </div>
          <div className="p-6">
            <EventViewer
              events={simulation.pending_events || []}
              actors={simulation.actors?.map(a => ({ id: a.id, name: a.name }))}
            />
          </div>
        </div>

        {/* Action Review Panel */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                ⚙️ Action Queue & Resolution
              </h2>
              <span className="px-2 py-1 text-xs rounded-full bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-400">
                {simulation.pending_actions?.length || 0} queued
              </span>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
              Monitor pending actions and review LLM-parsed intents. Outcomes appear after resolution phase.
            </p>
          </div>
          <div className="p-6">
            <ActionViewer
              actions={simulation.pending_actions || []}
              actors={simulation.actors?.map(a => ({ id: a.id, name: a.name }))}
            />
          </div>
        </div>

        {/* Phase Logs */}
        <PhaseLogViewer logs={simulation.phase_log || []} defaultExpanded={false} />
      </div>

      {/* Right Column: Action Composer & Actors */}
      <div className="space-y-4">
        {/* Action Composer */}
        <ActionComposer />

        {/* Actors Quick View */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="border-b border-gray-200 dark:border-gray-700 px-6 py-4">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              👥 Active Actors
            </h2>
          </div>
          <div className="p-6">
            <ActorManager simulationId={simulation.id} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Map View: Spatial visualization (placeholder for future implementation)
function MapView({ simulation }: { simulation: SimulationDetail }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-8">
      <div className="text-center">
        <div className="text-6xl mb-4">🗺️</div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          Map View Coming Soon
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Interactive map with Leaflet.js will display actor locations, event locations, and spatial relationships.
        </p>
        <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg text-left max-w-2xl mx-auto">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Planned Features:</h3>
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Interactive map with OpenStreetMap tiles</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Actor markers with popups showing details</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Event location markers with type-based icons</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Custom overlays for scenario-specific regions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Visibility rules based on researcher permissions</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-600 dark:text-green-400">✓</span>
              <span>Real-time updates as actors move and events occur</span>
            </li>
          </ul>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-6">
          Current simulation: <strong>{simulation.name}</strong> • {simulation.actors?.length || 0} actors ready for mapping
        </p>
      </div>
    </div>
  );
}

// Data View: Comprehensive data tables and analytics
function DataView({ simulation }: { simulation: SimulationDetail }) {
  const [activeDataTab, setActiveDataTab] = useState<'overview' | 'events' | 'actions' | 'actors' | 'logs'>('overview');

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      {/* Data Tab Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700">
        <div className="flex overflow-x-auto">
          {[
            { id: 'overview', label: 'Overview', icon: '📈' },
            { id: 'events', label: 'Events', icon: '⚡', count: simulation.pending_events?.length },
            { id: 'actions', label: 'Actions', icon: '⚙️', count: simulation.pending_actions?.length },
            { id: 'actors', label: 'Actors', icon: '👥', count: simulation.actors?.length },
            { id: 'logs', label: 'Logs', icon: '📝', count: simulation.phase_log?.length },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveDataTab(tab.id as any)}
              className={`px-6 py-3 font-medium text-sm whitespace-nowrap transition-colors ${
                activeDataTab === tab.id
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50'
              }`}
            >
              {tab.icon} {tab.label}
              {tab.count !== undefined && (
                <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                  activeDataTab === tab.id
                    ? 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        {activeDataTab === 'overview' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Simulation Details
                </h3>
                <dl className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-gray-600 dark:text-gray-400">Name:</dt>
                    <dd className="font-medium text-gray-900 dark:text-white">{simulation.name}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600 dark:text-gray-400">Scenario:</dt>
                    <dd className="font-medium text-gray-900 dark:text-white">{simulation.scenario}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600 dark:text-gray-400">Status:</dt>
                    <dd>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        simulation.status === 'running'
                          ? 'bg-green-100 dark:bg-green-900/20 text-green-800 dark:text-green-400'
                          : simulation.status === 'paused'
                          ? 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-400'
                      }`}>
                        {simulation.status.toUpperCase()}
                      </span>
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600 dark:text-gray-400">Created:</dt>
                    <dd className="font-medium text-gray-900 dark:text-white">
                      {simulation.created_at ? new Date(simulation.created_at).toLocaleString() : 'N/A'}
                    </dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-600 dark:text-gray-400">Last Updated:</dt>
                    <dd className="font-medium text-gray-900 dark:text-white">
                      {simulation.last_updated ? new Date(simulation.last_updated).toLocaleString() : 'N/A'}
                    </dd>
                  </div>
                </dl>
              </div>

              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Phase History
                </h3>
                <div className="space-y-1 max-h-40 overflow-y-auto">
                  {simulation.phase_history && simulation.phase_history.length > 0 ? (
                    simulation.phase_history.slice(-10).map((phase, index) => (
                      <div key={index} className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                        <span className="text-gray-400 dark:text-gray-600">#{simulation.phase_history.length - 10 + index + 1}</span>
                        <span className="flex-1">{phase.replace(/_/g, ' ')}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-gray-500 dark:text-gray-400 italic">No phase history yet</div>
                  )}
                </div>
              </div>
            </div>

            {simulation.phase_log && simulation.phase_log.length > 0 && (
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Recent Activity
                </h3>
                <div className="space-y-2">
                  {simulation.phase_log.slice(-3).reverse().map((log, index) => (
                    <div key={index} className="text-sm border-l-2 border-blue-400 dark:border-blue-600 pl-3 py-1">
                      <div className="font-medium text-gray-900 dark:text-white">{log.phase.replace(/_/g, ' ')}</div>
                      {log.notes && log.notes.length > 0 && (
                        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {log.notes[0]}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeDataTab === 'events' && (
          <EventViewer
            events={simulation.pending_events || []}
            actors={simulation.actors?.map(a => ({ id: a.id, name: a.name }))}
          />
        )}

        {activeDataTab === 'actions' && (
          <ActionViewer
            actions={simulation.pending_actions || []}
            actors={simulation.actors?.map(a => ({ id: a.id, name: a.name }))}
          />
        )}

        {activeDataTab === 'actors' && (
          <ActorManager simulationId={simulation.id} />
        )}

        {activeDataTab === 'logs' && (
          <PhaseLogViewer logs={simulation.phase_log || []} defaultExpanded={true} />
        )}
      </div>
    </div>
  );
}
