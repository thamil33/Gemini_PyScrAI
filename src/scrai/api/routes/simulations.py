"""Simulation management endpoints."""

from __future__ import annotations

from typing import Any, Dict, List, Set
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ..dependencies import get_runtime_manager
from ..schemas import (
    ActionCreateInput,
    ActionSummary,
    ActorSummary,
    AddActorInput,
    EventSummary,
    PhaseAdvanceResult,
    PhaseLogEntry,
    SimulationCreateInput,
    SimulationDetail,
    SimulationSummary,
    SimulationStreamEvent,
)
from ...models import Action, Actor, SimulationState
from ...models.action import ActionPriority, ActionType
from ...models.actor import ActorType
from ...models.simulation_state import SimulationPhase, SimulationStatus


router = APIRouter(prefix="/simulations", tags=["simulations"])


async def _load_simulation_or_404(runtime, simulation_id: str) -> SimulationState:
    simulation = await runtime.simulation_repository.get(simulation_id)
    if simulation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found",
        )
    return simulation


def _normalize_notes(notes: object) -> List[str]:
    if notes is None:
        return []
    if isinstance(notes, str):
        return [notes]
    if isinstance(notes, list):
        return [str(item) for item in notes]
    return [str(notes)]


async def build_simulation_detail(runtime, simulation: SimulationState) -> SimulationDetail:
    phase_log_entries: List[PhaseLogEntry] = []
    phase_history: List[str] = []

    for entry in simulation.metadata.get("phase_log", []):
        phase_value = entry.get("phase", simulation.current_phase.value)
        phase_history.append(phase_value)
        phase_log_entries.append(
            PhaseLogEntry(
                phase=phase_value,
                timestamp=entry.get("timestamp"),
                notes=_normalize_notes(entry.get("notes")),
            )
        )

    if not phase_history:
        phase_history = [simulation.current_phase.value]

    pending_actions: List[ActionSummary] = []
    actor_ids: Set[str] = set(simulation.active_actor_ids)
    for action_id in simulation.pending_action_ids:
        action = await runtime.action_repository.get(action_id)
        if not action:
            continue
        actor_ids.add(action.actor_id)
        pending_actions.append(
            ActionSummary(
                id=action.id,
                actor_id=action.actor_id,
                intent=action.intent,
                description=action.description,
                status=action.status.value,
                priority=action.priority.value,
                created_at=action.created_at,
                metadata=action.metadata,
            )
        )

    pending_actions.sort(key=lambda item: item.created_at)

    pending_events: List[EventSummary] = []
    for event_id in simulation.pending_event_ids:
        event = await runtime.event_repository.get(event_id)
        if not event:
            continue
        pending_events.append(
            EventSummary(
                id=event.id,
                title=event.title,
                description=event.description,
                status=event.status.value,
                type=event.type.value,
                created_at=event.created_at,
                scheduled_for=event.scheduled_for,
            )
        )

    pending_events.sort(key=lambda item: item.created_at)

    for summary in pending_events:
        event = await runtime.event_repository.get(summary.id)
        if event:
            actor_ids.update(event.affected_actors)

    actors: List[ActorSummary] = []
    for actor_id in actor_ids:
        actor = await runtime.actor_repository.get(actor_id)
        if not actor:
            continue
        actors.append(
            ActorSummary(
                id=actor.id,
                name=actor.name,
                type=actor.type.value,
                active=actor.active,
                last_updated=actor.updated_at,
            )
        )

    actors.sort(key=lambda item: item.name.lower())

    return SimulationDetail(
        id=simulation.id,
        name=simulation.name,
        scenario=simulation.scenario_module,
        status=simulation.status.value,
        current_phase=simulation.current_phase.value,
        phase_number=simulation.phase_number,
        pending_action_count=len(simulation.pending_action_ids),
        pending_event_count=len(simulation.pending_event_ids),
        created_at=simulation.created_at,
        last_updated=simulation.updated_at,
        phase_history=phase_history,
        phase_log=phase_log_entries,
        actors=actors,
        pending_actions=pending_actions,
        pending_events=pending_events,
        metadata=simulation.metadata,
    )


def build_simulation_summary(simulation: SimulationState) -> SimulationSummary:
    """Construct a SimulationSummary from the simulation state."""

    return SimulationSummary(
        id=simulation.id,
        name=simulation.name,
        status=simulation.status.value,
        current_phase=simulation.current_phase.value,
        phase_number=simulation.phase_number,
        pending_action_count=len(simulation.pending_action_ids),
        pending_event_count=len(simulation.pending_event_ids),
        last_updated=simulation.updated_at,
    )


async def _publish_simulation_event(
    runtime_manager,
    simulation: SimulationState,
    event_name: str,
    detail: SimulationDetail,
    summary: SimulationSummary,
    *,
    phase_result: PhaseAdvanceResult | None = None,
    metadata: Dict[str, Any] | None = None,
) -> None:
    """Publish an SSE event to connected clients for this simulation."""

    event = SimulationStreamEvent(
        event=event_name,
        simulation_id=simulation.id,
        ts=datetime.now(timezone.utc),
        detail=detail,
        summary=summary,
        phase_result=phase_result,
        metadata=metadata or {},
    )
    await runtime_manager.publish_stream_event(
        simulation.id,
        event.model_dump(mode="json"),
    )


@router.post("", response_model=SimulationDetail, status_code=status.HTTP_201_CREATED)
async def create_simulation(input_data: SimulationCreateInput) -> SimulationDetail:
    """Create a new simulation."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    
    # Generate unique ID
    sim_id = f"sim-{uuid.uuid4().hex[:8]}"
    
    # Create simulation state
    simulation = SimulationState(
        id=sim_id,
        name=input_data.name,
        scenario_module=input_data.scenario,
        current_phase=SimulationPhase.INITIALIZE,
        phase_number=0,
        status=SimulationStatus.CREATED,
    )
    
    # Save to repository
    await runtime.simulation_repository.create(simulation)

    detail = await build_simulation_detail(runtime, simulation)
    summary = build_simulation_summary(simulation)
    await _publish_simulation_event(
        runtime_manager,
        simulation,
        "simulation.created",
        detail,
        summary,
    )

    return detail


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_simulation(simulation_id: str) -> None:
    """Delete a simulation."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()

    # Check if simulation exists
    simulation = await runtime.simulation_repository.get(simulation_id)
    if simulation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found",
        )

    # Delete from repository
    deleted = await runtime.simulation_repository.delete(simulation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete simulation",
        )


@router.get("", response_model=List[SimulationSummary])
async def list_simulations() -> List[SimulationSummary]:
    """List all simulations."""
    runtime = get_runtime_manager().get_runtime()
    
    simulations = await runtime.simulation_repository.list_all()
    
    return [build_simulation_summary(sim) for sim in simulations]


@router.get("/{simulation_id}", response_model=SimulationDetail)
async def get_simulation(simulation_id: str) -> SimulationDetail:
    """Get simulation details."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    
    simulation = await _load_simulation_or_404(runtime, simulation_id)

    return await build_simulation_detail(runtime, simulation)


@router.post("/{simulation_id}/start", response_model=SimulationDetail)
async def start_simulation(simulation_id: str) -> SimulationDetail:
    """Start a simulation."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    sim_lock = runtime_manager.get_simulation_lock(simulation_id)
    
    async with sim_lock:
        simulation = await _load_simulation_or_404(runtime, simulation_id)

        # Update status to running
        simulation.start()
        updates = {
            "status": simulation.status.value,
            "updated_at": simulation.updated_at.isoformat(),
        }
        if simulation.started_at:
            updates["started_at"] = simulation.started_at.isoformat()
        await runtime.simulation_repository.update(simulation.id, updates)

    updated_simulation = await runtime.simulation_repository.get(simulation_id)
    if updated_simulation is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulation disappeared after start",
        )

    detail = await build_simulation_detail(runtime, updated_simulation)
    summary = build_simulation_summary(updated_simulation)
    await _publish_simulation_event(
        runtime_manager,
        updated_simulation,
        "simulation.started",
        detail,
        summary,
    )
    return detail


@router.post("/{simulation_id}/advance", response_model=PhaseAdvanceResult)
async def advance_simulation(simulation_id: str) -> PhaseAdvanceResult:
    """Advance simulation to next phase."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    sim_lock = runtime_manager.get_simulation_lock(simulation_id)
    
    updated_sim: SimulationState | None = None
    phase_response: PhaseAdvanceResult | None = None

    async with sim_lock:
        simulation = await _load_simulation_or_404(runtime, simulation_id)

        previous_phase = simulation.current_phase.value

        # Execute phase advancement
        try:
            await runtime.phase_engine.step(simulation.id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Phase advancement failed: {str(e)}"
            )

        # Reload updated simulation
        updated_sim = await runtime.simulation_repository.get(simulation_id)
        if updated_sim is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Simulation disappeared after phase advance"
            )

        phase_response = PhaseAdvanceResult(
            simulation_id=updated_sim.id,
            previous_phase=previous_phase,
            current_phase=updated_sim.current_phase.value,
            phase_number=updated_sim.phase_number,
            status=updated_sim.status.value,
            message=f"Advanced from {previous_phase} to {updated_sim.current_phase.value}",
        )

    assert updated_sim is not None and phase_response is not None

    detail = await build_simulation_detail(runtime, updated_sim)
    summary = build_simulation_summary(updated_sim)
    await _publish_simulation_event(
        runtime_manager,
        updated_sim,
        "simulation.phase_advanced",
        detail,
        summary,
        phase_result=phase_response,
    )

    return phase_response


@router.post(
    "/{simulation_id}/actions",
    response_model=SimulationDetail,
    status_code=status.HTTP_201_CREATED,
)
async def inject_action(simulation_id: str, input_data: ActionCreateInput) -> SimulationDetail:
    """Inject a new action into a simulation and return the updated detail."""

    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()
    sim_lock = runtime_manager.get_simulation_lock(simulation_id)

    async with sim_lock:
        simulation = await _load_simulation_or_404(runtime, simulation_id)

        actor = await runtime.actor_repository.get(input_data.actor_id)
        if actor is None:
            actor = Actor(
                id=input_data.actor_id,
                name=input_data.metadata.get("actor_name", input_data.actor_id),
                type=ActorType.NPC,
            )
            await runtime.actor_repository.create(actor)
            simulation.add_actor(actor.id)

        action_id = f"act-{uuid.uuid4().hex[:10]}"
        metadata = dict(input_data.metadata)
        action = Action(
            id=action_id,
            actor_id=actor.id,
            simulation_id=simulation_id,
            type=ActionType.CUSTOM,
            intent=input_data.intent,
            description=input_data.description or input_data.intent,
            priority=ActionPriority.NORMAL,
            metadata=metadata,
        )

        await runtime.action_repository.create(action)
        simulation.add_pending_action(action.id)
        await runtime.simulation_repository.update(simulation.id, simulation.to_dict())

    updated_simulation = await runtime.simulation_repository.get(simulation_id)
    if updated_simulation is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulation disappeared after action injection",
        )

    detail = await build_simulation_detail(runtime, updated_simulation)
    summary = build_simulation_summary(updated_simulation)
    await _publish_simulation_event(
        runtime_manager,
        updated_simulation,
        "simulation.action_added",
        detail,
        summary,
        metadata={"action_id": action.id},
    )
    return detail


@router.post(
    "/{simulation_id}/actors",
    response_model=SimulationDetail,
    status_code=status.HTTP_201_CREATED,
)
async def add_actor_to_simulation(
    simulation_id: str, input_data: AddActorInput
) -> SimulationDetail:
    """Add an existing actor to a simulation's active actor list."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()

    simulation = await _load_simulation_or_404(runtime, simulation_id)

    # Verify actor exists
    actor = await runtime.actor_repository.get(input_data.actor_id)
    if actor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor {input_data.actor_id} not found",
        )

    # Add actor to simulation if not already present
    if input_data.actor_id not in simulation.active_actor_ids:
        simulation.add_actor(input_data.actor_id)
        await runtime.simulation_repository.update(simulation.id, simulation.to_dict())

    # Reload and return updated simulation
    updated_simulation = await runtime.simulation_repository.get(simulation_id)
    if updated_simulation is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Simulation disappeared after adding actor",
        )

    detail = await build_simulation_detail(runtime, updated_simulation)
    summary = build_simulation_summary(updated_simulation)
    await _publish_simulation_event(
        runtime_manager,
        updated_simulation,
        "simulation.actor_added",
        detail,
        summary,
        metadata={"actor_id": input_data.actor_id},
    )
    return detail
