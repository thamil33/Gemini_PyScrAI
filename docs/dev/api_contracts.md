# ScrAI API Contracts

## Repository Interface Contracts

### Base Repository Interface

All repositories implement the generic `Repository[T]` interface:

```python
class Repository(ABC, Generic[T]):
    async def create(entity: T) -> str
    async def get(entity_id: str) -> Optional[T]
    async def update(entity_id: str, updates: Dict[str, Any]) -> bool
    async def delete(entity_id: str) -> bool
    async def list_all(limit: Optional[int] = None) -> List[T]
    async def query(filters: Dict[str, Any], limit: Optional[int] = None) -> List[T]
    async def exists(entity_id: str) -> bool
```

### Error Handling

All repository methods may raise `RepositoryError` with context:
- `message`: Error description
- `operation`: Operation being performed (create, get, update, delete, etc.)
- `entity_type`: Type of entity (Actor, Event, Action, SimulationState)
- `entity_id`: ID of the entity (if applicable)

### Actor Repository Contract

**Collection**: `actors`

**Specialized Methods**:
- `find_by_type(actor_type: ActorType) -> List[Actor]`
- `find_by_name(name: str) -> Optional[Actor]`
- `find_active() -> List[Actor]`
- `find_in_location(location_field: str, location_value: Any) -> List[Actor]`
- `find_by_affiliation(affiliation: str) -> List[Actor]`

### Event Repository Contract

**Collection**: `events`

**Specialized Methods**:
- `find_by_status(status: EventStatus) -> List[Event]`
- `find_by_type(event_type: EventType) -> List[Event]`
- `find_pending_approval() -> List[Event]`
- `find_by_actor(actor_id: str) -> List[Event]`
- `find_recent(hours: int = 24) -> List[Event]`

### Action Repository Contract

**Collection**: `actions`

**Specialized Methods**:
- `find_by_actor(actor_id: str) -> List[Action]`
- `find_by_status(status: ActionStatus) -> List[Action]`
- `find_by_type(action_type: ActionType) -> List[Action]`
- `find_by_priority(priority: ActionPriority) -> List[Action]`
- `find_pending_approval() -> List[Action]`
- `find_pending_execution() -> List[Action]`
- `find_active() -> List[Action]`

### Simulation Repository Contract

**Collection**: `simulations`

**Specialized Methods**:
- `find_by_status(status: SimulationStatus) -> List[SimulationState]`
- `find_by_scenario(scenario_module: str) -> List[SimulationState]`
- `find_running() -> List[SimulationState]`
- `find_completed() -> List[SimulationState]`
- `find_by_name(name: str) -> Optional[SimulationState]`

## LLM Service Contract

### Service Interface

The high-level `LLMService` exposes a provider-agnostic interface for generating completions:

```python
class LLMService:
    async def complete(
        self,
        messages: Iterable[LLMMessage | Mapping[str, str]],
        *,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse

    async def list_models(self, provider: Optional[str] = None) -> List[str]

    async def validate(self) -> bool

    async def close(self) -> None
```

- `complete` attempts the configured provider chain (primary + fallbacks) until one succeeds, returning an `LLMResponse` or raising the last error.
- `list_models` returns available model identifiers for the specified provider.
- `validate` verifies connectivity for every configured provider.
- `close` releases any underlying HTTP sessions.

### Provider Configuration

Providers are configured with `ProviderConfig` dataclasses:

```python
@dataclass(slots=True)
class ProviderConfig:
    name: str                      # e.g. "openrouter", "lmstudio", "lm_proxy"
    model: Optional[str] = None    # default derived from provider if omitted
    base_url: Optional[str] = None # overrides default endpoint
    api_key: Optional[str] = None  # pulled from env if omitted
    api_key_header: str = "Authorization"
    timeout: int = 30
    max_retries: int = 3
    extra_headers: Dict[str, str] = field(default_factory=dict)
    provider_label: Optional[str] = None
```

An `LLMServiceConfig` combines a primary provider and optional fallbacks. The default setup draws from environment variables (`SCRAI_LLM_*`, `OPENROUTER_*`, etc.).

### Provider Implementations

The `OpenAICompatibleClient` class supports OpenRouter, LM Studio, LM Proxy, and any other OpenAI-compatible endpoints via configurable `base_url`, `model`, and headers. Future providers (e.g., Google Gemini) can implement their own `LLMClient` subclasses without changing callers.

## Phase Engine Contract

### PhaseEngine Interface

```python
class PhaseEngine:
    async def step(
        self,
        simulation_id: str,
        *,
        force_phase: Optional[SimulationPhase] = None,
    ) -> PhaseResult

    async def run_cycle(self, simulation_id: str) -> List[PhaseResult]
```

- `step` executes a single phase for the specified simulation, optionally forcing a particular phase. It returns a `PhaseResult` describing the executed phase, next phase, and metadata.
- `run_cycle` advances the simulation through the canonical phase order (Initialize → Event Generation → Action Collection → Action Resolution → World Update → Snapshot) until the cycle completes or the simulation reaches a terminal state.

### PhaseResult Structure

```python
@dataclass(slots=True)
class PhaseResult:
    simulation: SimulationState
    executed_phase: SimulationPhase
    next_phase: SimulationPhase
    generated_event_ids: List[str]
    generated_action_ids: List[str]
    notes: List[str]
```

- `simulation` is the mutated `SimulationState` after the phase completes.
- `executed_phase` indicates which phase handler ran.
- `next_phase` identifies the phase the simulation expects next.
- `notes` contains human-readable status messages persisted (when enabled) to `simulation.metadata["phase_log"]`.

### Phase Handlers

Each phase has a dedicated handler implementing the `BasePhaseHandler` interface. The default registry includes:

| Phase | Handler | Responsibility |
| --- | --- | --- |
| `INITIALIZE` | `InitializePhaseHandler` | Start/resume simulations and prepare initial state |
| `EVENT_GENERATION` | `EventGenerationPhaseHandler` | Seeds/updates scenario entities and orchestrates scenario-driven event generation |
| `ACTION_COLLECTION` | `ActionCollectionPhaseHandler` | Aggregate pending actions from the repository |
| `ACTION_RESOLUTION` | `ActionResolutionPhaseHandler` | Placeholder for applying action outcomes |
| `WORLD_UPDATE` | `WorldUpdatePhaseHandler` | Placeholder for updating world state from events |
| `SNAPSHOT` | `SnapshotPhaseHandler` | Record simulation snapshots and advance phase counters |

Custom handlers can be supplied to `PhaseEngine` via the `handlers` constructor argument to override default behavior.

### Persistence Guarantees

After each phase the engine persists the latest `SimulationState` via `SimulationRepository.update`. Failures to persist raise `PhaseEngineError`. Notes from the phase can be recorded automatically when `PhaseEngineConfig.persist_phase_notes` is `True` (default).

### PhaseEngineConfig

```python
@dataclass(slots=True)
class PhaseEngineConfig:
    persist_phase_notes: bool = True
    enforce_phase_sequence: bool = True
    max_consecutive_failures: int = 3
```

- `persist_phase_notes` controls whether phase log entries are appended to simulation metadata.
- `enforce_phase_sequence` raises an error when phases are executed out of order.
- `max_consecutive_failures` is reserved for future automatic retry logic.

## Scenario Service Contract

### Scenario Components

```python
class Scenario(ABC):
    name: str

    @abstractmethod
    def seed(self, context: ScenarioContext) -> None: ...

    def before_phase(self, context: ScenarioContext) -> None: ...
    def after_phase(self, context: ScenarioContext) -> None: ...
    def on_snapshot(self, context: ScenarioContext) -> None: ...
```

- `ScenarioContext` holds the live `SimulationState` plus mutable collections of `Actor`, `Event`, and `Action` instances. Scenario modules mutate the context by calling `context.extend(...)`.
- `ScenarioRegistry` maintains a keyed mapping of scenario instances and prevents duplicate registrations.
- `ScenarioService` selects scenarios, seeds initial entities, and invokes lifecycle hooks (`before_phase`, `after_phase`, `on_snapshot`).

### Event Generation Lifecycle

- On first entry to the Event Generation phase, the engine calls `ScenarioService.seed_scenario`, persists any new actors/events/actions, and marks the simulation metadata as seeded.
- For subsequent Event Generation passes, the handler reconstructs `ScenarioContext` from the simulation's active and pending IDs, invokes `scenario.before_phase`, and persists any newly added entities.
- `generated_event_ids` and `generated_action_ids` in the `PhaseResult` reflect entities persisted during the phase.

### Default Scenario Service

The helper `scrai.scenarios.create_default_scenario_service()` registers the built-in `SimpleTownScenario`, which seeds a small community with a mayor, doctor, caretaker, and morning briefing event/action. Applications may register additional scenarios or replace the service entirely when instantiating the `PhaseEngine`.
## Firestore Implementation Details

### Collections Structure

```
/actors/{actor_id}
/events/{event_id}
/actions/{action_id}
/simulations/{simulation_id}
```

### Automatic Fields

All documents automatically receive:
- `created_at`: Timestamp when document is created
- `updated_at`: Timestamp when document is last modified
- `id`: Document ID is also stored in the document

### Query Limitations

Firestore has limitations on complex queries:
- Array membership queries require special handling
- Nested field queries are limited
- Some queries fall back to in-memory filtering

### Error Handling

Firestore-specific errors are caught and converted to `RepositoryError`:
- `GoogleAPICallError`: Firestore API failures
- Connection timeouts and network issues
- Permission and authentication errors

## Usage Examples

### Basic CRUD Operations

```python
# Initialize repositories
firestore_client = FirestoreClient(project_id="my-project")
await firestore_client.initialize()

actor_repo = ActorRepository(firestore_client)

# Create
actor = Actor(id="actor1", name="John", type=ActorType.PLAYER)
actor_id = await actor_repo.create(actor)

# Read
retrieved_actor = await actor_repo.get("actor1")

# Update
await actor_repo.update("actor1", {"name": "John Doe"})

# Delete
await actor_repo.delete("actor1")
```

### Specialized Queries

```python
# Find all NPCs
npcs = await actor_repo.find_by_type(ActorType.NPC)

# Find pending events
pending_events = await event_repo.find_by_status(EventStatus.PENDING)

# Find actions by specific actor
actor_actions = await action_repo.find_by_actor("actor1")
```