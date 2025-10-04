// Phase log viewer component

import { useState } from 'react';
import { useSimulationStore } from '../stores/simulationStore';
import type { PhaseLogEntry } from '../types/api';

export function PhaseLogViewer() {
  const { activeSimulation } = useSimulationStore();
  const [isExpanded, setIsExpanded] = useState(false);

  if (!activeSimulation || activeSimulation.phase_log.length === 0) {
    return null;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <svg
            className={`w-5 h-5 text-gray-500 dark:text-gray-400 transition-transform ${
              isExpanded ? 'rotate-90' : ''
            }`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Phase Log
          </h3>
          <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
            {activeSimulation.phase_log.length} entries
          </span>
        </div>
        {!isExpanded && (
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Click to expand
          </span>
        )}
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700">
          <div className="p-6 space-y-4 max-h-96 overflow-y-auto">
            {activeSimulation.phase_log.map((entry: PhaseLogEntry, index: number) => (
              <div
                key={index}
                className="border-l-4 border-blue-500 dark:border-blue-400 pl-4 py-2"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white">
                    {entry.phase.replace(/_/g, ' ').toUpperCase()}
                  </h4>
                  {entry.timestamp && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                  )}
                </div>
                {entry.notes && entry.notes.length > 0 && (
                  <ul className="space-y-1">
                    {entry.notes.map((note: string, noteIndex: number) => (
                      <li
                        key={noteIndex}
                        className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2"
                      >
                        <span className="text-gray-400 dark:text-gray-600 mt-1">•</span>
                        <span>{note}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
