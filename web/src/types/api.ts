// API Types matching backend schemas

export interface SimulationCreateInput {
  name: string;
  scenario: string;
}

export interface PhaseLogEntry {
  phase: string;
  timestamp: string | null;
  notes: string[];
}

export interface ActorSummary {
  id: string;
  name: string;
  type: string;
  active: boolean;
  last_updated: string | null;
}

export interface ActionSummary {
  id: string;
  actor_id: string;
  intent: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  metadata: Record<string, unknown>;
}

export interface EventSummary {
  id: string;
  title: string;
  description: string;
  status: string;
  type: string;
  created_at: string;
  scheduled_for: string | null;
}

export interface SimulationSummary {
  id: string;
  name: string;
  status: string;
  current_phase: string;
  phase_number: number;
  pending_action_count: number;
  pending_event_count: number;
  last_updated: string | null;
}

export interface SimulationDetail {
  id: string;
  name: string;
  scenario: string;
  status: string;
  current_phase: string;
  phase_number: number;
  pending_action_count: number;
  pending_event_count: number;
  created_at: string | null;
  last_updated: string | null;
  phase_history: string[];
  phase_log: PhaseLogEntry[];
  actors: ActorSummary[];
  pending_actions: ActionSummary[];
  pending_events: EventSummary[];
  metadata: Record<string, unknown>;
}

export interface PhaseAdvanceResult {
  simulation_id: string;
  previous_phase: string;
  current_phase: string;
  phase_number: number;
  status: string;
  message: string;
}

export interface SimulationStreamEvent {
  event: string;
  simulation_id: string;
  ts: string;
  detail?: SimulationDetail;
  summary?: SimulationSummary;
  phase_result?: PhaseAdvanceResult;
  metadata?: Record<string, unknown>;
}

export interface ActionCreateInput {
  actorId: string;
  intent: string;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface ActorCreateInput {
  name: string;
  type: string;
  attributes?: Record<string, unknown>;
  location?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface ActorUpdateInput {
  name?: string;
  type?: string;
  active?: boolean;
  attributes?: Record<string, unknown>;
  location?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface ActorDetail {
  id: string;
  name: string;
  type: string;
  active: boolean;
  attributes: Record<string, unknown>;
  location?: Record<string, unknown>;
  visibility: Record<string, unknown>;
  relationships: Record<string, unknown>;
  affiliations: string[];
  created_at: string | null;
  last_updated: string | null;
  metadata: Record<string, unknown>;
}

export interface ErrorResponse {
  error_type: string;
  detail: string;
}

export interface LLMStatusResponse {
  available: boolean;
  ready: boolean;
  providers: string[];
  detail?: string | null;
}
