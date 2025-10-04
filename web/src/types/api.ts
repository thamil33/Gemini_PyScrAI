// API Types matching backend schemas

// Enums matching backend
export enum EventType {
  ENVIRONMENTAL = 'environmental',
  SOCIAL = 'social',
  ECONOMIC = 'economic',
  POLITICAL = 'political',
  SYSTEM = 'system',
  PLAYER_ACTION = 'player_action',
  NPC_ACTION = 'npc_action',
}

export enum EventStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  RESOLVED = 'resolved',
  CANCELLED = 'cancelled',
}

export enum ActionType {
  MOVEMENT = 'movement',
  COMMUNICATION = 'communication',
  INTERACTION = 'interaction',
  ECONOMIC = 'economic',
  SOCIAL = 'social',
  COMBAT = 'combat',
  RESEARCH = 'research',
  CUSTOM = 'custom',
}

export enum ActionStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  EXECUTING = 'executing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export enum ActionPriority {
  LOW = 'low',
  NORMAL = 'normal',
  HIGH = 'high',
  URGENT = 'urgent',
}

export enum ActorType {
  PLAYER = 'player',
  NPC = 'npc',
  SYSTEM = 'system',
}

export enum SimulationStatus {
  CREATED = 'created',
  RUNNING = 'running',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  ERROR = 'error',
}

export enum SimulationPhase {
  INITIALIZE = 'initialize',
  EVENT_GENERATION = 'event_generation',
  ACTION_COLLECTION = 'action_collection',
  ACTION_RESOLUTION = 'action_resolution',
  WORLD_UPDATE = 'world_update',
  SNAPSHOT = 'snapshot',
}

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
  type: ActorType | string;
  active: boolean;
  last_updated: string | null;
  location?: Record<string, unknown> | null;
  attributes?: Record<string, unknown>;
}

export interface ActionSummary {
  id: string;
  actor_id: string;
  simulation_id?: string | null;
  intent: string;
  description: string;
  status: ActionStatus | string;
  priority: ActionPriority | string;
  type?: ActionType | string;
  created_at: string;
  metadata: Record<string, unknown>;
  outcome?: string | null;
}

export interface ActionDetail {
  id: string;
  actor_id: string;
  simulation_id: string | null;
  type: ActionType | string;
  intent: string;
  description: string;
  parameters: Record<string, unknown>;
  target_actor_ids: string[];
  target_location: Record<string, unknown> | null;
  status: ActionStatus | string;
  priority: ActionPriority | string;
  created_at: string;
  scheduled_for: string | null;
  started_at: string | null;
  completed_at: string | null;
  llm_parsed: boolean;
  parsed_options: Array<Record<string, unknown>>;
  selected_option: number | null;
  prerequisites: string[];
  resource_costs: Record<string, unknown>;
  success_probability: number | null;
  outcome: string | null;
  generated_events: string[];
  requires_approval: boolean;
  approved_by: string | null;
  modifications: Array<Record<string, unknown>>;
  source: string;
  metadata: Record<string, unknown>;
}

export interface EventSummary {
  id: string;
  title: string;
  description: string;
  status: EventStatus | string;
  type: EventType | string;
  created_at: string;
  scheduled_for: string | null;
  affected_actors?: string[];
  location?: Record<string, unknown>;
  source?: string;
  trigger_action_id?: string | null;
}

export interface EventDetail {
  id: string;
  title: string;
  description: string;
  type: EventType | string;
  status: EventStatus | string;
  created_at: string;
  scheduled_for: string | null;
  resolved_at: string | null;
  affected_actors: string[];
  location: Record<string, unknown> | null;
  scope: string;
  parameters: Record<string, unknown>;
  effects: Record<string, unknown>;
  source: string;
  trigger_event_id: string | null;
  trigger_action_id: string | null;
  requires_approval: boolean;
  approved_by: string | null;
  modifications: Array<Record<string, unknown>>;
  metadata: Record<string, unknown>;
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
  type: ActorType | string;
  active: boolean;
  attributes: Record<string, unknown>;
  location: Record<string, unknown> | null;
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
