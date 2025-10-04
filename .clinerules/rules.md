# ScrAI AI Agent Guide

## Current Focus (Phase 2)
- Deliver the **Milestone 3 action workflow** described in `docs/dev/phase_2.md`: `POST /api/simulations/{id}/actions`, `/api/llm/check`, richer simulation detail payloads, and the React `ActionComposer` UX.
- Prepare the codebase for Milestone 4 SSE streaming while keeping the existing polling fallback stable.
- Keep CLI and API behaviour aligned—leverage the shared runtime (`api/dependencies.py`, `cli/runtime.py`) and extend pytest coverage when adding endpoints.

## Documentation Map
- `docs/blueprint.md`: Long-term roadmap, high-level phase expectations.
- `docs/dev/phase_2.md`: Source of truth for Phase 2 status, milestones, and active task clusters (updated October 2025).
- `docs/dev/api_contracts.md`: Repository and API contract details—synchronize changes when new endpoints or fields are added.
- `docs/dev/state_transitions.md`: Simulation lifecycle diagrams; consult when altering phase sequencing or status transitions.
- `docs/addendum_I.md`: LLM configuration goals for future extensibility.

## Architecture
- Backend code lives in `src/scrai`; `api/app.py` bootstraps FastAPI and registers `routes/simulations.py` under `/api` while injecting a process-wide `RuntimeManager`.
- `RuntimeManager` (see `api/dependencies.py`) ensures a single `RuntimeContext` built from `cli/runtime.py`; respect this singleton so repos, `PhaseEngine`, and configuration stay in sync.
- `PhaseEngine` (`engine/phase_engine.py`) coordinates the cycle INITIALIZE → EVENT_GENERATION → ACTION_COLLECTION → ACTION_RESOLUTION → WORLD_UPDATE → SNAPSHOT using handler classes in `engine/phase_handlers.py`.
- Scenario logic is delegated to `scenarios`; the default `SimpleTownScenario` seeds actors/events during the first Event Generation pass and subsequent cycles reload context from repositories.
- Data persistence layers implement the async `Repository` interface (`data/repository.py`); memory-backed implementations in `cli/memory.py` share a JSON store, while Firestore repos rely on `data/firestore_client.py`.

## Domain Conventions
- Work with Pydantic models in `models/`; prefer invoking helpers such as `SimulationState.add_pending_action`, `.record_snapshot`, or `Action.complete` so timestamps and lists stay consistent.
- Repository methods are `async`; awaiting them inside FastAPI handlers and phase logic is required to avoid state loss.
- `SimulationState.to_dict()` uses `model_dump(mode="json")`; any new fields must remain JSON-serializable (datetimes become ISO strings).
- When adding phases or altering the cycle, update `_DEFAULT_PHASE_ORDER` in `PhaseEngine` and ensure a corresponding handler is registered in `PhaseHandlerRegistry`.
- Frontend clients use snake_case keys defined in `web/src/types/api.ts`; keep API schemas in `api/schemas.py` aligned to avoid breaking the Vite UI.

## Developer Workflows
- Start the API with `python run_api.py` (uvicorn reloads on changes); health lives at `/health` and `/api/simulations` powers both CLI and web.
- Use the CLI entrypoint `scrai` (registered in `pyproject.toml`) or `python -m scrai.cli.main`; the memory backend persists to `~/.scrai/state.json` unless `--state-path` is provided.
- Standard tests run with `pytest`; `tests/test_cli.py` exercises the memory flow, and `python tests/test_integration.py` spins up uvicorn separately to verify HTTP + CLI parity.
- Frontend lives in `web/`; run `npm install` then `npm run dev` to proxy `/api` to `http://localhost:8000` as configured in `vite.config.ts`.
- Preconfigured settings live in `config/settings.toml`; overrides can be supplied with `SCRAI_*` env vars that `config/settings.py` loads via `load_settings`.

## Implementation Tips
- Acquire per-simulation locks through `RuntimeManager.get_simulation_lock` when mutating shared state; skipping the lock can interleave phase executions.
- The default runtime sets `llm_service=None`; wire up an `LLMService` (see `llm/service.py`) before invoking LLM-dependent hooks, otherwise phase handlers treat LLM interaction as optional.
- Memory repositories bypass Firestore-specific filters; if you add new query helpers ensure both memory and Firestore variants are implemented or guarded.
- When extending API responses, update both response schemas and the front-end store in `web/src/stores/simulationStore.ts` to keep polling logic consistent.
- Emit lightweight deltas for SSE (Milestone 4) to avoid overloading the client; reuse DTOs already defined for polling responses.

## Testing Expectations
- Extend or mirror tests in `tests/test_integration.py` whenever new API endpoints are added to guarantee CLI ↔ API parity.
- For frontend additions, create Vitest/RTL coverage around stores and components, and document manual SSE + polling smoke checks in PR descriptions.
- Keep `pytest --cov=scrai` green; investigate coverage dips before merging.
