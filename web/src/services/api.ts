// API client service for simulation endpoints

import type {
  SimulationCreateInput,
  SimulationSummary,
  SimulationDetail,
  PhaseAdvanceResult,
  ErrorResponse,
  ActionCreateInput,
  LLMStatusResponse,
} from '../types/api';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(
    public status: number,
    public errorType: string,
    public detail: string
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: ErrorResponse;
    try {
      errorData = await response.json();
    } catch {
      throw new ApiError(response.status, 'unknown', response.statusText);
    }
    throw new ApiError(response.status, errorData.error_type, errorData.detail);
  }
  return response.json();
}

export const simulationService = {
  async createSimulation(input: SimulationCreateInput): Promise<SimulationDetail> {
    const response = await fetch(`${API_BASE}/simulations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return handleResponse<SimulationDetail>(response);
  },

  async listSimulations(): Promise<SimulationSummary[]> {
    const response = await fetch(`${API_BASE}/simulations`);
    return handleResponse<SimulationSummary[]>(response);
  },

  async getSimulation(id: string): Promise<SimulationDetail> {
    const response = await fetch(`${API_BASE}/simulations/${id}`);
    return handleResponse<SimulationDetail>(response);
  },

  async startSimulation(id: string): Promise<SimulationDetail> {
    const response = await fetch(`${API_BASE}/simulations/${id}/start`, {
      method: 'POST',
    });
    return handleResponse<SimulationDetail>(response);
  },

  async advanceSimulation(id: string): Promise<PhaseAdvanceResult> {
    const response = await fetch(`${API_BASE}/simulations/${id}/advance`, {
      method: 'POST',
    });
    return handleResponse<PhaseAdvanceResult>(response);
  },

  async submitAction(id: string, input: ActionCreateInput): Promise<SimulationDetail> {
    const payload = {
      actor_id: input.actorId,
      intent: input.intent,
      description: input.description,
      metadata: input.metadata,
    };
    const response = await fetch(`${API_BASE}/simulations/${id}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return handleResponse<SimulationDetail>(response);
  },
};

export { ApiError };

export const llmService = {
  async checkStatus(): Promise<LLMStatusResponse> {
    const response = await fetch(`${API_BASE}/llm/check`, {
      method: 'POST',
    });
    return handleResponse<LLMStatusResponse>(response);
  },
};

// Generic API client for other endpoints
export const api = {
  async get<T>(path: string): Promise<{ data: T }> {
    const response = await fetch(`${API_BASE}${path}`);
    const data = await handleResponse<T>(response);
    return { data };
  },
};
