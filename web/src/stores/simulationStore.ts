// Zustand store for simulation state management

import { create } from 'zustand';
import type {
  SimulationSummary,
  SimulationDetail,
  ActionCreateInput,
  SimulationStreamEvent,
  ActorSummary,
  ActorCreateInput,
  ActorUpdateInput,
  ActorDetail,
} from '../types/api';
import { simulationService } from '../services/api';
import { connectToSimulationStream } from '../lib/sse';
import { useToastStore } from './toastStore';

interface SimulationState {
  // Data
  simulations: SimulationSummary[];
  activeSimulation: SimulationDetail | null;
  currentStreamId: string | null;
  lastHeartbeat: string | null;

  // UI State
  isFetching: boolean;
  isActionSubmitting: boolean;
  error: string | null;
  connection: 'polling' | 'sse' | 'offline';

  // Actions
  fetchSimulations: () => Promise<void>;
  selectSimulation: (id: string) => Promise<void>;
  createSimulation: (name: string, scenario: string) => Promise<void>;
  startSimulation: (id: string) => Promise<void>;
  advanceSimulation: (id: string) => Promise<void>;
  submitAction: (id: string, input: ActionCreateInput) => Promise<void>;
  fetchActors: () => Promise<ActorSummary[]>;
  createActor: (input: ActorCreateInput) => Promise<ActorDetail>;
  updateActor: (id: string, input: ActorUpdateInput) => Promise<ActorDetail>;
  deleteActor: (id: string) => Promise<void>;
  deleteSimulation: (id: string) => Promise<void>;
  clearError: () => void;
  startPolling: () => void;
  stopPolling: () => void;
  connectStream: (id: string) => void;
  disconnectStream: () => void;
  handleStreamEvent: (event: SimulationStreamEvent) => void;
}

let pollInterval: ReturnType<typeof setInterval> | null = null;
const STREAM_BACKOFF_BASE_MS = 2000;
const STREAM_BACKOFF_MAX_MS = 30000;

let currentStream: EventSource | null = null;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let reconnectAttempts = 0;

const deriveSummaryFromDetail = (detail: SimulationDetail): SimulationSummary => ({
  id: detail.id,
  name: detail.name,
  status: detail.status,
  current_phase: detail.current_phase,
  phase_number: detail.phase_number,
  pending_action_count: detail.pending_action_count,
  pending_event_count: detail.pending_event_count,
  last_updated: detail.last_updated,
});

const upsertSummary = (
  entries: SimulationSummary[],
  summary: SimulationSummary
): SimulationSummary[] => {
  const index = entries.findIndex((item) => item.id === summary.id);
  if (index === -1) {
    return [...entries, summary];
  }
  const next = entries.slice();
  next[index] = summary;
  return next;
};

export const useSimulationStore = create<SimulationState>((set, get) => ({
  // Initial state
  simulations: [],
  activeSimulation: null,
  currentStreamId: null,
  lastHeartbeat: null,
  isFetching: false,
  isActionSubmitting: false,
  error: null,
  connection: 'polling',

  // Fetch all simulations
  fetchSimulations: async () => {
    set({ isFetching: true, error: null });
    try {
      const simulations = await simulationService.listSimulations();
      set({ simulations, isFetching: false });
    } catch (error) {
      set({ error: (error as Error).message, isFetching: false });
    }
  },

  // Select and load simulation details
  selectSimulation: async (id: string) => {
    set({ isFetching: true, error: null });
    try {
      const simulation = await simulationService.getSimulation(id);
      set((state) => ({
        activeSimulation: simulation,
        isFetching: false,
        simulations: upsertSummary(state.simulations, deriveSummaryFromDetail(simulation)),
      }));
      get().connectStream(id);
    } catch (error) {
      set({ error: (error as Error).message, isFetching: false });
    }
  },

  // Create new simulation
  createSimulation: async (name: string, scenario: string) => {
    set({ isFetching: true, error: null });
    try {
      const simulation = await simulationService.createSimulation({ name, scenario });
      set((state) => ({
        activeSimulation: simulation,
        isFetching: false,
        simulations: upsertSummary(state.simulations, deriveSummaryFromDetail(simulation)),
      }));
      get().connectStream(simulation.id);
      useToastStore.getState().success(`Simulation "${name}" created successfully`);
      // Refresh list
      await get().fetchSimulations();
    } catch (error) {
      const errorMessage = (error as Error).message;
      set({ error: errorMessage, isFetching: false });
      useToastStore.getState().error(`Failed to create simulation: ${errorMessage}`);
    }
  },

  // Start simulation
  startSimulation: async (id: string) => {
    set({ isFetching: true, error: null });
    try {
      const simulation = await simulationService.startSimulation(id);
      set((state) => ({
        activeSimulation: simulation,
        isFetching: false,
        simulations: upsertSummary(state.simulations, deriveSummaryFromDetail(simulation)),
      }));
      get().connectStream(simulation.id);
      useToastStore.getState().success('Simulation started');
      await get().fetchSimulations();
    } catch (error) {
      const errorMessage = (error as Error).message;
      set({ error: errorMessage, isFetching: false });
      useToastStore.getState().error(`Failed to start simulation: ${errorMessage}`);
    }
  },

  // Advance simulation phase
  advanceSimulation: async (id: string) => {
    set({ isFetching: true, error: null });
    try {
      await simulationService.advanceSimulation(id);
      // Reload simulation details
      const simulation = await simulationService.getSimulation(id);
      set((state) => ({
        activeSimulation: simulation,
        isFetching: false,
        simulations: upsertSummary(state.simulations, deriveSummaryFromDetail(simulation)),
      }));
      await get().fetchSimulations();
    } catch (error) {
      set({ error: (error as Error).message, isFetching: false });
    }
  },

  submitAction: async (id: string, input: ActionCreateInput) => {
    set({ isActionSubmitting: true, error: null });
    try {
      const simulation = await simulationService.submitAction(id, input);
      set((state) => ({
        activeSimulation: simulation,
        isActionSubmitting: false,
        simulations: upsertSummary(state.simulations, deriveSummaryFromDetail(simulation)),
      }));
      useToastStore.getState().success('Action submitted successfully');
      await get().fetchSimulations();
    } catch (error) {
      const errorMessage = (error as Error).message;
      set({ error: errorMessage, isActionSubmitting: false });
      useToastStore.getState().error(`Failed to submit action: ${errorMessage}`);
      throw error;
    }
  },

  // Clear error
  clearError: () => set({ error: null }),

  // Start polling for updates
  startPolling: () => {
    if (pollInterval) return;
    
    const poll = async () => {
      const state = get();
      await state.fetchSimulations();

      if (state.connection === 'sse') {
        return;
      }

      const active = state.activeSimulation;
      if (!active) {
        return;
      }

      try {
        const simulation = await simulationService.getSimulation(active.id);
        set((current) => ({
          activeSimulation: simulation,
          simulations: upsertSummary(
            current.simulations,
            deriveSummaryFromDetail(simulation)
          ),
        }));
      } catch (error) {
        set({ error: (error as Error).message });
      }
    };

    pollInterval = setInterval(poll, 4000);
    void poll();
  },

  // Stop polling
  stopPolling: () => {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  },

  connectStream: (id: string) => {
    if (!id) {
      return;
    }

    if (get().currentStreamId === id && currentStream) {
      return;
    }

    if (currentStream) {
      currentStream.close();
      currentStream = null;
    }

    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    reconnectAttempts = 0;
    set({ currentStreamId: id });

    const source = connectToSimulationStream(id, {
      onOpen: () => {
        reconnectAttempts = 0;
        set({ connection: 'sse' });
        get().stopPolling();
      },
      onEvent: (payload) => {
        get().handleStreamEvent(payload);
      },
      onHeartbeat: (timestamp) => set({ lastHeartbeat: timestamp }),
      onError: () => {
        if (currentStream === source) {
          currentStream.close();
          currentStream = null;
        }

        const delay = Math.min(
          STREAM_BACKOFF_MAX_MS,
          STREAM_BACKOFF_BASE_MS * 2 ** reconnectAttempts
        );
        reconnectAttempts += 1;

        if (reconnectTimer) {
          clearTimeout(reconnectTimer);
        }

        reconnectTimer = setTimeout(() => {
          reconnectTimer = null;
          const { currentStreamId } = get();
          if (currentStreamId) {
            get().connectStream(currentStreamId);
          }
        }, delay);

        set({ connection: 'offline' });
        get().startPolling();
      },
    });

    currentStream = source;
  },

  disconnectStream: () => {
    if (currentStream) {
      currentStream.close();
      currentStream = null;
    }

    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    reconnectAttempts = 0;
    set({ currentStreamId: null, lastHeartbeat: null, connection: 'polling' });
    get().startPolling();
  },

  handleStreamEvent: (event: SimulationStreamEvent) => {
    const summary =
      event.summary ?? (event.detail ? deriveSummaryFromDetail(event.detail) : undefined);

    set((state) => {
      const simulations = summary
        ? upsertSummary(state.simulations, summary)
        : state.simulations;

      let activeSimulation = state.activeSimulation;
      if (event.detail) {
        if (!activeSimulation || activeSimulation.id === event.simulation_id) {
          activeSimulation = event.detail;
        }
      }

      return {
        simulations,
        activeSimulation,
        connection: 'sse',
        lastHeartbeat: event.ts,
        isFetching: false,
        isActionSubmitting: false,
        error: null,
      };
    });
  },

  // Actor management methods
  fetchActors: async () => {
    try {
      const response = await fetch('/api/actors');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const actors = await response.json();
      return actors as ActorSummary[];
    } catch (error) {
      console.error('Failed to fetch actors:', error);
      throw error;
    }
  },

  createActor: async (input: ActorCreateInput) => {
    try {
      // Create the actor globally
      const response = await fetch('/api/actors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const actor = await response.json() as ActorDetail;
      
      // Add the actor to the current simulation if one is active
      const { activeSimulation } = get();
      if (activeSimulation) {
        const addResponse = await fetch(
          `/api/simulations/${activeSimulation.id}/actors`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ actor_id: actor.id }),
          }
        );
        if (!addResponse.ok) {
          throw new Error(`Failed to add actor to simulation: ${addResponse.status}`);
        }
        const updatedSimulation = await addResponse.json() as SimulationDetail;
        set((state) => ({
          activeSimulation: updatedSimulation,
          simulations: upsertSummary(
            state.simulations,
            deriveSummaryFromDetail(updatedSimulation)
          ),
        }));
      }
      
      return actor;
    } catch (error) {
      console.error('Failed to create actor:', error);
      throw error;
    }
  },

  updateActor: async (id: string, input: ActorUpdateInput) => {
    try {
      const response = await fetch(`/api/actors/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(input),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const actor = await response.json();
      return actor as ActorDetail;
    } catch (error) {
      console.error('Failed to update actor:', error);
      throw error;
    }
  },

  deleteActor: async (id: string) => {
    try {
      const response = await fetch(`/api/actors/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to delete actor:', error);
      throw error;
    }
  },

  deleteSimulation: async (id: string) => {
    try {
      const response = await fetch(`/api/simulations/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Failed to delete simulation:', error);
      throw error;
    }
  },
}));
