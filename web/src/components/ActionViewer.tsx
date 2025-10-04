// Action viewer component

import { ActionSummary, ActionStatus, ActionPriority, ActionType } from '../types/api';

interface ActionViewerProps {
  actions: ActionSummary[];
  actors?: Array<{ id: string; name: string }>;
}

export function ActionViewer({ actions, actors }: ActionViewerProps) {
  if (actions.length === 0) {
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400 italic">
        No actions yet
      </div>
    );
  }

  const getActorName = (actorId: string) => {
    const actor = actors?.find(a => a.id === actorId);
    return actor?.name || actorId;
  };

  const getStatusColor = (status: ActionStatus | string) => {
    switch (status) {
      case ActionStatus.PENDING:
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case ActionStatus.APPROVED:
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case ActionStatus.EXECUTING:
        return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      case ActionStatus.COMPLETED:
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case ActionStatus.FAILED:
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      case ActionStatus.CANCELLED:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const getPriorityColor = (priority: ActionPriority | string) => {
    switch (priority) {
      case ActionPriority.URGENT:
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 border-red-300 dark:border-red-700';
      case ActionPriority.HIGH:
        return 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 border-orange-300 dark:border-orange-700';
      case ActionPriority.NORMAL:
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 border-blue-300 dark:border-blue-700';
      case ActionPriority.LOW:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 border-gray-300 dark:border-gray-600';
    }
  };

  const getActionTypeIcon = (type?: ActionType | string) => {
    switch (type) {
      case ActionType.MOVEMENT:
        return '🚶';
      case ActionType.COMMUNICATION:
        return '💬';
      case ActionType.INTERACTION:
        return '🤝';
      case ActionType.ECONOMIC:
        return '💰';
      case ActionType.SOCIAL:
        return '👥';
      case ActionType.COMBAT:
        return '⚔️';
      case ActionType.RESEARCH:
        return '🔬';
      default:
        return '📋';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-3">
      {actions.map((action) => (
        <div
          key={action.id}
          className={`border-l-4 ${getPriorityColor(action.priority)} bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-r-lg p-4 hover:shadow-md transition-shadow`}
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-lg">{getActionTypeIcon(action.type)}</span>
                <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                  {getActorName(action.actor_id)}
                </span>
              </div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                {action.intent}
              </h4>
              <div className="flex gap-2 flex-wrap">
                <span className={`text-xs px-2 py-1 rounded ${getStatusColor(action.status)}`}>
                  {action.status}
                </span>
                {action.type && (
                  <span className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
                    {action.type}
                  </span>
                )}
              </div>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
              {formatTimestamp(action.created_at)}
            </div>
          </div>

          {action.description && (
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
              {action.description}
            </p>
          )}

          {action.outcome && (
            <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-900 rounded border border-gray-200 dark:border-gray-700">
              <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                Outcome:
              </div>
              <div className="text-sm text-gray-800 dark:text-gray-200">
                {action.outcome}
              </div>
            </div>
          )}

          {action.metadata && Object.keys(action.metadata).length > 0 && (
            <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              <details>
                <summary className="cursor-pointer hover:text-gray-700 dark:hover:text-gray-300">
                  Metadata
                </summary>
                <pre className="mt-1 p-2 bg-gray-50 dark:bg-gray-900 rounded text-xs overflow-x-auto">
                  {JSON.stringify(action.metadata, null, 2)}
                </pre>
              </details>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
