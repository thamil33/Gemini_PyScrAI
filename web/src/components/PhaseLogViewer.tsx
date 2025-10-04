// Phase log viewer component

import { useState } from 'react';
import type { PhaseLogEntry } from '../types/api';

interface PhaseLogViewerProps {
  logs: PhaseLogEntry[];
  defaultExpanded?: boolean;
  maxHeight?: string;
}

export function PhaseLogViewer({ logs, defaultExpanded = false, maxHeight = '96' }: PhaseLogViewerProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (!logs || logs.length === 0) {
    return (
      <div className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg text-center">
        <p className="text-gray-500 dark:text-gray-400 text-sm">No phase logs available yet.</p>
        <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">Logs will appear as the simulation progresses through phases.</p>
      </div>
    );
  }

  const getPhaseColor = (phase: string) => {
    const phaseColors: Record<string, string> = {
      'initialize': 'border-gray-500 dark:border-gray-400',
      'event_generation': 'border-purple-500 dark:border-purple-400',
      'action_collection': 'border-blue-500 dark:border-blue-400',
      'action_resolution': 'border-orange-500 dark:border-orange-400',
      'world_update': 'border-green-500 dark:border-green-400',
      'snapshot': 'border-cyan-500 dark:border-cyan-400',
    };
    return phaseColors[phase.toLowerCase()] || 'border-gray-500 dark:border-gray-400';
  };

  const getPhaseIcon = (phase: string) => {
    const phaseIcons: Record<string, string> = {
      'initialize': '🚀',
      'event_generation': '⚡',
      'action_collection': '📥',
      'action_resolution': '⚙️',
      'world_update': '🌍',
      'snapshot': '📸',
    };
    return phaseIcons[phase.toLowerCase()] || '📋';
  };

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
            Phase Execution Log
          </h3>
          <span className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-full">
            {logs.length} entries
          </span>
        </div>
        {!isExpanded && logs.length > 0 && (
          <span className="text-sm text-gray-500 dark:text-gray-400">
            Latest: {logs[logs.length - 1].phase.replace(/_/g, ' ')}
          </span>
        )}
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700">
          <div className={`p-6 space-y-4 max-h-${maxHeight} overflow-y-auto`}>
            {logs.map((entry: PhaseLogEntry, index: number) => (
              <div
                key={index}
                className={`border-l-4 ${getPhaseColor(entry.phase)} pl-4 py-2 bg-gray-50 dark:bg-gray-900 rounded-r-lg`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <span>{getPhaseIcon(entry.phase)}</span>
                    <span>{entry.phase.replace(/_/g, ' ').toUpperCase()}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 font-normal">
                      (Entry #{index + 1})
                    </span>
                  </h4>
                  {entry.timestamp && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {new Date(entry.timestamp).toLocaleString()}
                    </span>
                  )}
                </div>
                
                {entry.notes && entry.notes.length > 0 ? (
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
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-500 italic">
                    No detailed notes for this phase execution.
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
