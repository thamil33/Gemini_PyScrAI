import { useMemo } from 'react';
import { useSimulationStore } from '../stores/simulationStore';

const STATUS_MAP = {
  sse: {
    label: 'Live updates',
    dot: 'bg-emerald-500',
    text: 'text-emerald-600 dark:text-emerald-300',
  },
  polling: {
    label: 'Polling fallback',
    dot: 'bg-amber-500',
    text: 'text-amber-600 dark:text-amber-300',
  },
  offline: {
    label: 'Reconnecting…',
    dot: 'bg-rose-500',
    text: 'text-rose-600 dark:text-rose-300',
  },
} as const;

type ConnectionKey = keyof typeof STATUS_MAP;

export function ConnectionStatusBadge() {
  const { connection, lastHeartbeat } = useSimulationStore((state) => ({
    connection: state.connection as ConnectionKey,
    lastHeartbeat: state.lastHeartbeat,
  }));

  const heartbeatText = useMemo(() => {
    if (!lastHeartbeat || connection !== 'sse') {
      return null;
    }
    try {
      const formatted = new Date(lastHeartbeat).toLocaleTimeString();
      return `Heartbeat ${formatted}`;
    } catch {
      return null;
    }
  }, [lastHeartbeat, connection]);

  const config = STATUS_MAP[connection] ?? STATUS_MAP.polling;

  return (
    <div className="flex items-center gap-2 rounded-full border border-gray-200 dark:border-gray-700 bg-white/60 dark:bg-gray-900/40 px-3 py-1 text-xs sm:text-sm">
      <span className={`h-2.5 w-2.5 rounded-full ${config.dot}`}></span>
      <span className={`font-medium ${config.text}`}>{config.label}</span>
      {heartbeatText && (
        <span className="hidden sm:inline text-gray-500 dark:text-gray-400">
          {heartbeatText}
        </span>
      )}
    </div>
  );
}
