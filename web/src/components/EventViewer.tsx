// Event viewer component

import { EventSummary, EventStatus, EventType } from '../types/api';

interface EventViewerProps {
  events: EventSummary[];
  actors?: Array<{ id: string; name: string }>;
}

export function EventViewer({ events, actors }: EventViewerProps) {
  if (events.length === 0) {
    return (
      <div className="text-sm text-gray-500 dark:text-gray-400 italic">
        No events yet
      </div>
    );
  }

  const getActorName = (actorId: string) => {
    const actor = actors?.find(a => a.id === actorId);
    return actor?.name || actorId;
  };

  const getEventTypeColor = (type: EventType | string) => {
    switch (type) {
      case EventType.SOCIAL:
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case EventType.ENVIRONMENTAL:
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case EventType.ECONOMIC:
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case EventType.POLITICAL:
        return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200';
      case EventType.SYSTEM:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const getStatusColor = (status: EventStatus | string) => {
    switch (status) {
      case EventStatus.PENDING:
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case EventStatus.CONFIRMED:
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case EventStatus.RESOLVED:
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      case EventStatus.CANCELLED:
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string | null) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="space-y-3">
      {events.map((event) => (
        <div
          key={event.id}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between gap-3 mb-2">
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-1">
                {event.title}
              </h4>
              <div className="flex gap-2 flex-wrap mb-2">
                <span className={`text-xs px-2 py-1 rounded ${getEventTypeColor(event.type)}`}>
                  {event.type}
                </span>
                <span className={`text-xs px-2 py-1 rounded ${getStatusColor(event.status)}`}>
                  {event.status}
                </span>
              </div>
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
              {formatTimestamp(event.created_at)}
            </div>
          </div>

          <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
            {event.description}
          </p>

          <div className="flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
            {event.affected_actors && event.affected_actors.length > 0 && (
              <div>
                <span className="font-medium">Affects: </span>
                {event.affected_actors.map(actorId => getActorName(actorId)).join(', ')}
              </div>
            )}
            
            {event.location && (
              <div>
                <span className="font-medium">Location: </span>
                {(event.location as any).name || 'Unknown'}
              </div>
            )}

            {event.source && (
              <div>
                <span className="font-medium">Source: </span>
                {event.source}
              </div>
            )}

            {event.scheduled_for && (
              <div>
                <span className="font-medium">Scheduled: </span>
                {formatTimestamp(event.scheduled_for)}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
