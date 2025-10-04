# ScrAI Phase 2: Web UI & API Layer Implementation

## Overview

**Phase 2 Goals:** Transform ScrAI from a CLI-only tool into a comprehensive web application that provides an intuitive, real-time interface for simulation management. This phase focuses on delivering the earliest functional UI that can operate real simulations, then iterating quickly while maintaining the research-grade capabilities of the backend system.

**Execution Horizon:** 10-14 days for lean MVP delivery
**Target Interface:** Web-based simulation dashboard with real-time controls (incremental enhancement)
**Complexity Level:** Moderate (focused scope, fast iteration, sustainable maintenance)

## Current Status (October 4, 2025)

- ✅ **Milestone 1 – Bootstrap**: FastAPI service, runtime singleton, and initial `/api/simulations` CRUD endpoints are live and validated through the CLI parity tests.
- ✅ **Milestone 2 – UI Shell**: Vite + React + Tailwind shell, Zustand polling store, and manual phase controls are in place; the dashboard consumes the memory backend successfully.
- ✅ **Milestone 3 – Real LLM Interaction**: Action injection + LLM readiness endpoints are live, Action Composer UX ships with validation, and simulation detail payloads carry pending action/event context.
- 🎯 **Milestone 4 – SSE Increment**: `/api/streams/simulations/{id}` stream, publisher hooks, and the hybrid SSE + polling client with connection status badge are landed; upcoming work focuses on delta shaping and log hydration.
- ♻️ **Core workflows**: CLI and API share the same runtime; pytest coverage for CLI ↔ API parity is running green.
- 🛰️ **Follow-ups**: Map foundations (Milestone 5) and quality refinement (Milestone 6) remain scoped but unstarted.

## Locked Preferences

- **Authentication:** Open access for Phase 2 (no auth/RBAC layer yet)
- **LLM Integration:** Use the existing `lm_proxy` provider exactly as configured today
- **Delivery Mindset:** Optimize for earliest working UI, layering polish and depth in subsequent passes

## Architecture Decisions

### 1. Tech Stack Selection

#### Backend API
- **Framework:** FastAPI ✅ (chosen over Flask for automatic OpenAPI docs, async support, and performance)
- **Benefits:**
  - Native async support for real-time simulation operations
  - Automatic API documentation generation
  - Type validation and serialization
  - High-performance async request handling
  - Excellent for long-running simulation operations

#### Frontend Architecture
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite (fast development server, optimized production builds)
- **State Management:** Zustand (lightweight, intuitive, perfect for moderate complexity)
- **Real-time Communication:** Server-Sent Events (SSE) for live updates

#### Styling Solution
- **Framework:** Tailwind CSS ⭐ **RECOMMENDED**
- **Benefits:**
  - Utility-first approach speeds development
  - Consistent design system built-in
  - Responsive mobile-first approach
  - Small bundle size (only includes used utilities)
  - Perfect for research/simulation interfaces
  - Easy custom color scheme integration

### 2. Project Structure

```
scrai/
├── api/                    # FastAPI backend
│   ├── __init__.py
│   ├── app.py             # Main FastAPI app
│   ├── routes/            # Route handlers
│   ├── dependencies.py    # Common dependencies
│   ├── middleware.py      # Custom middleware
│   └── schemas/           # Pydantic models for API
├── web/                    # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── stores/        # Zustand stores
│   │   ├── services/      # API client services
│   │   ├── types/         # TypeScript types
│   │   └── lib/           # Utilities and constants
│   ├── public/
│   ├── package.json
│   └── tailwind.config.js
├── docker/
│   ├── Dockerfile.api
│   └── Dockerfile.web
└── docker-compose.yml      # Development environment
```

## Development Phases

### Milestone Plan (Lean Delivery)

**Milestone 1 – Bootstrap (Day 1-2) ✅ Completed**
- Create `api/` package with FastAPI app, `/health`, and basic `/simulations` CRUD
- Add async runtime builder (convert `build_runtime` pattern to non-blocking)
- Ship memory backend only; introduce Firestore toggle later
- Endpoint scope: `POST /simulations`, `GET /simulations`, `GET /simulations/{id}`, `POST /simulations/{id}/start`, `POST /simulations/{id}/advance`
- Surface simple phase log passthrough for UI consumption

**Milestone 2 – UI Shell (Day 2-4) ✅ Completed**
- Scaffold Vite + React + Tailwind with `DashboardLayout`, `SimulationList`, `ActiveSimulationPanel`
- Implement basic Zustand store with 3–5s polling cadence
- Display phase badge plus pending actions/events counts
- Wire manual advance/start buttons targeting Milestone 1 endpoints

**Milestone 3 – Real LLM Interaction (Day 4-6) ✅ Completed**
- API: `POST /simulations/{id}/actions` ships with auto actor creation + repository wiring
- `/api/llm/check` surfaces provider readiness and degrades gracefully when unconfigured
- Frontend `ActionComposer` submits intents with validation + optimistic UI refresh
- Integration tests cover the new endpoints alongside existing CLI parity checks

**Milestone 4 – SSE Increment (Day 6-8) 🎯 In Progress**
- `/api/streams/simulations/{id}` streams simulation envelopes via SSE with heartbeats
- Runtime publishers broadcast updates on create/start/advance/action mutations
- Frontend EventSource client with reconnect/backoff complements polling fallback and surfaces connection status
- Next: trim payload deltas and feed phase log viewer / notification toasts

**Milestone 5 – Map Base (Day 8-10) 🔜 Upcoming**
- Standardize `Actor.location` contract: `{ name: str, lat: float | None, lon: float | None }`
- Render Leaflet map with markers (only for actors with coordinates; cluster logical nodes otherwise)
- Color markers by `actor.type`

**Milestone 6 – Quality & Refinement (Day 10-14) 🔜 Upcoming**
- Add loading/error states across API interactions
- Implement phase cycle button (snapshot loop → reset to initialize)
- Inline phase log viewer and dark-mode toggle
- Harden SSE payload size/heartbeat to mitigate backpressure

## Active Task Clusters (Phase 2)

### 1. Action Flow & LLM Validation (Milestone 3) ✅ Shipped
- CLI-compatible `POST /api/simulations/{id}/actions` mirrors auto actor creation, repository writes, and pending action wiring.
- `/api/llm/check` provides provider readiness without raising on configuration gaps.
- `SimulationDetail` + frontend types expose pending actions/events and phase logging for researcher review.
- `ActionComposer` UX delivers validated submissions with optimistic refresh and integration coverage was extended.

### 2. Real-time Delivery (Milestone 4) 🎯 In Progress
- ✅ `/api/streams/simulations/{id}` streams simulation envelopes with runtime publishers triggering on create/start/advance/action mutations.
- ✅ Frontend EventSource client manages reconnect/backoff, updates the Zustand store, and surfaces a connection status badge while retaining polling fallback.
- ⏭️ Next: trim SSE payloads into targeted deltas, pipe phase log entries into the UI, and add toast notifications on critical stream events.

### 3. Visualization & UX Depth (Milestones 5-6)
- Normalize actor location metadata, update `SimpleTownScenario`, and supply map-friendly data shapes.
- Integrate React-Leaflet for simulation maps, color markers by actor type, and provide a list fallback when coordinates are missing.
- Embed a phase log viewer, full-cycle run control, and dark-mode toggle consistent with Tailwind theme tokens.
- Harden SSE payloads, logging, and error surfacing to support research mediation workflows.

## API Design

### Core Endpoints

```python
# Simulation Management (Milestone 1 foundation)
POST   /api/simulations               # Create new simulation (name, scenario)
GET    /api/simulations               # List simulations
GET    /api/simulations/{id}          # Retrieve simulation details
POST   /api/simulations/{id}/start    # Begin simulation execution
POST   /api/simulations/{id}/advance  # Advance simulation phase

# Action Flow (Milestone 3)
POST   /api/simulations/{id}/actions  # Inject new action (auto-create actors as needed)
POST   /api/llm/check                 # Validate intent via lm_proxy-backed service

# Real-time Updates (Milestone 4)
GET    /api/streams/simulations/{id}  # SSE stream with phase/action/event envelopes
```

### Real-time Communication Strategy

- **Server-Sent Events (SSE):** Primary transport for live simulation updates post-Milestone 4
- **Hybrid Polling:** Maintain 3–5s polling fallback for legacy browsers or SSE dropouts
- **Connection Management:** Automatic reconnection with exponential backoff, heartbeat every 15s
- **Event Envelope:** `simulation.snapshot`, `simulation.started`, `simulation.action_added`, `simulation.phase_advanced`, plus heartbeats carry `summary` + optional `detail` payloads

## Frontend Component Architecture

### Core Components

```typescript
// Dashboard Components
- DashboardLayout: Main layout wrapper
- SimulationList: Table/cards of simulations
- ActiveSimulationPanel: Status, phase badge, metrics
- ControlButtons: Start/Advance actions

// Action Components
- ActionComposer: Intent submission form
- PhaseLogViewer: Inline log history (Milestone 6)

// Map Components
- SimulationMap: Leaflet container
- ActorMarker: Marker decorator (color by actor.type)
- ActorCluster: Logical grouping when coordinates missing

// Utility Components
- ConnectionStatus: SSE/polling indicator
- ErrorBanner: Surface API/SSE failures
```

### State Management Strategy

```typescript
// Zustand Store Structure (hybrid SSE + polling)
interface SimulationState {
  simulations: SimulationSummary[]
  activeSimulation: Simulation | null
  currentStreamId: string | null
  lastHeartbeat: string | null
  isFetching: boolean
  isActionSubmitting: boolean
  error: string | null
  connection: 'polling' | 'sse' | 'offline'
}

// Actions
- fetchSimulations()
- selectSimulation(id: string)
- createSimulation(name: string, scenario: string)
- startSimulation(id: string)
- advanceSimulation(id: string)
- submitAction(id: string, input: ActionCreateInput)
- connectStream(id: string)
- disconnectStream()
- handleStreamEvent(event: SimulationStreamEvent)
```

## Design System & Styling

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Simulation-specific colors
        phase: {
          initialize: '#3B82F6',    // blue
          event_gen: '#8B5CF6',     // violet
          action_collect: '#F59E0B', // amber
          action_resolve: '#EF4444',  // red
          world_update: '#10B981',    // emerald
          snapshot: '#06B6D4',        // cyan
        },
        // Status colors
        status: {
          pending: '#F59E0B',
          active: '#10B981',
          completed: '#3B82F6',
          error: '#EF4444',
        }
      },
      // Custom utilities for simulation UI
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Component Styling Patterns

```jsx
// Consistent card styling
<div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
    Simulation Status
  </h3>
  {/* Content */}
</div>

// Button patterns
<button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors">
  Advance Phase
</button>

// Status indicators
<span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
  Active
</span>
```

## Integration Strategy

### Backend API Integration

1. **API Client Layer**
  - Lightweight fetch wrappers or Axios with interceptors for error normalization
  - No auth headers required in Phase 2 (open access)
  - Shared response transformers to match frontend DTO contracts

2. **Real-time Updates**
  - SSE subscriber that dispatches to Zustand via `handleSseEvent`
  - Polling fallback reuses the same update actions to keep logic unified
  - Connection status stored to drive UI indicators

3. **Error Handling**
  - Global error boundary + toast notifications
  - Structured API errors: `{error_type, detail}`
  - LLM timeouts return `{error_type: "llm_timeout"}` for user-friendly feedback

### Data Flow Architecture

```typescript
// Service Layer (fetch-based example)
const simulationService = {
  createSimulation: (payload: SimulationCreateInput) => post('/api/simulations', payload),
  listSimulations: () => get<SimulationSummary[]>('/api/simulations'),
  getSimulation: (id: string) => get<Simulation>(`/api/simulations/${id}`),
  start: (id: string) => post(`/api/simulations/${id}/start`),
  advance: (id: string) => post(`/api/simulations/${id}/advance`),
  submitAction: (id: string, input: ActionCreateInput) => post(`/api/simulations/${id}/actions`, input),
  checkLlm: (payload: LlmCheckInput) => post('/api/llm/check', payload),
}

// Store Layer sketch
const useSimulationStore = create<SimulationState>((set, get) => ({
  simulations: [],
  activeSimulation: null,
  isFetching: false,
  error: null,
  connection: 'polling',
  fetchSimulations: async () => {
    set({ isFetching: true })
    try {
      const sims = await simulationService.listSimulations()
      set({ simulations: sims, isFetching: false })
    } catch (error) {
      set({ error: toMessage(error), isFetching: false })
    }
  },
  handleSseEvent: (event) => {
    const { activeSimulation } = get()
    // merge payloads into store state depending on event.type
  },
}))
```

## Deployment Strategy

### Development Environment
- Prefer standalone FastAPI + Vite dev servers for speed; optional Docker Compose once both stabilize
- Reuse existing `.env` values and `settings.toml`; no new secrets required for Phase 2
- Configure CORS for `http://localhost:3000`

### Production Deployment
- **API:** Google Cloud Run (reuse container from dev once stable)
- **Web:** Netlify/Vercel static hosting
- **Database:** In-memory for Phase 2 MVP; Firestore toggle added post-Milestone 6

## Testing Strategy

### Backend Testing
- Pytest with `httpx.AsyncClient` for endpoint verification (memory backend)
- Runtime smoke test compares CLI vs API behavior for shared scenarios

### Frontend Testing
- Vitest + React Testing Library for critical components
- Playwright happy-path flows after Milestone 4

### Quality Gates for MVP
- Manual smoke: run CLI + UI against same memory simulations daily
- SSE fallback verified by forcing network errors in dev tools

## Success Metrics

### Technical Metrics
- **Performance:** Page load <2s, interactions <100ms
- **Accessibility:** WCAG AA compliance
- **Mobile:** Responsive across screen sizes
- **Real-time:** Update latency <500ms

### User Experience Metrics
- **Usability:** Task completion rates >90%
- **Learnability:** New user onboarding time <15 minutes
- **Satisfaction:** Research productivity improvement
- **Reliability:** Error rate <1% of interactions

## Risk Mitigation

- **Prevent engine overlap:** Guard phase execution with `asyncio.Lock` within runtime service
- **SSE backpressure:** Emit minimal payloads, avoid dumping full repositories per event
- **LLM timeout tolerance:** 30s timeout, degrade with `{error_type: "llm_timeout"}` responses and UI toast

### Deferrals (Explicitly Out of Scope for Phase 2)
- Authentication / RBAC
- Firestore scaling and tuning
- Background job queue
- Full geospatial validation
- Multi-tab collaborative conflict resolution

### Runtime Refactor Snapshot

```python
async def create_runtime(backend: str = "memory") -> RuntimeHandle:
  """Assemble repositories and phase engine without blocking event loop."""
  # build repositories asynchronously, reuse existing configuration
  ...

runtime_singleton = RuntimeSingleton(factory=create_runtime)
```

- Singleton instantiated lazily per process; `asyncio.Lock` per simulation prevents overlapping `advance` calls
- CLI and API both call through this layer to ensure behavior parity

### Data Contracts (Initial Stable Set)

- **Simulation Detail DTO:**
  ```json
  {
    "id": "sim-1234",
    "name": "string",
    "scenario": "string",
    "status": "created|running|paused|completed|error",
    "current_phase": "initialize|event_generation|...",
    "phase_number": 0,
    "pending_action_count": 0,
    "pending_event_count": 0,
    "created_at": "2025-10-04T12:34:56Z",
    "last_updated": "2025-10-04T12:34:56Z",
    "phase_history": ["initialize", "event_generation"],
    "phase_log": [{"phase": "initialize", "timestamp": "...", "notes": ["..."]}],
    "actors": [{"id": "actor-1", "name": "Mayor", "type": "npc", "active": true }],
    "pending_actions": [{"id": "act-1", "intent": "Collect samples", "status": "pending", "priority": "normal", "created_at": "..."}],
    "pending_events": [{"id": "evt-1", "title": "Morning Brief", "status": "pending", "created_at": "..."}],
    "metadata": {"phase_log": [...]} 
  }
  ```
- **Action Create Input:** `{ actor_id, intent, description?, metadata? }`
- **LLM Status Response:** `{ available: bool, ready: bool, providers: string[], detail?: string }`
- **SSE Event Envelope:** `{ event: string, simulation_id: string, data: object, ts: iso8601 }`

## Conclusion

This Phase 2 plan provides a comprehensive roadmap for transforming ScrAI from a CLI tool into a professional web application. The moderate complexity approach balances feature richness with development efficiency, ensuring research-grade capabilities in an accessible web interface.

**Key Success Factors:**
- Lean milestones that deliver usable software every 2-3 days
- Shared runtime layer that keeps CLI and UI in lockstep
- Real-time UX resilience via SSE + fallback strategy
- Early LLM integration using existing `lm_proxy` provider

**Next Steps:**
1. Confirm Milestone 1 scope and owners
2. Stand up FastAPI skeleton + async runtime factory
3. Create Vite + Tailwind shell to consume `/health`
4. Schedule daily sync for milestone demos and adjustments
