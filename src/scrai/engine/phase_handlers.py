"""Phase handler implementations for the ScrAI simulation engine."""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ..models import Action, Actor, Event, SimulationState
from ..models.action import ActionStatus, ActionType
from ..models.event import EventStatus, EventType
from ..models.simulation_state import SimulationPhase, SimulationStatus
from ..scenarios import ScenarioContext
from ..llm.base import LLMMessage
from .context import PhaseContext, PhaseResult
from .llm_prompts import (
    build_simulation_context,
    parse_llm_json_response,
    safe_get_dict,
    safe_get_list,
    safe_get_str,
    ACTION_RESOLUTION_PROMPT,
    EVENT_GENERATION_PROMPT,
    WORLD_UPDATE_PROMPT,
)

logger = logging.getLogger(__name__)


class BasePhaseHandler(ABC):
    """Abstract base class for all phase handlers."""

    phase: SimulationPhase

    def __init__(self, *, name: Optional[str] = None):
        self.name = name or self.__class__.__name__

    @abstractmethod
    async def run(self, context: PhaseContext) -> PhaseResult:
        """Execute the phase and return the resulting state."""

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"{self.__class__.__name__}(phase={self.phase})"


class PhaseHandlerRegistry:
    """Registry mapping simulation phases to handler implementations."""

    def __init__(self, handlers: Iterable[BasePhaseHandler]):
        self._handlers: Dict[SimulationPhase, BasePhaseHandler] = {}
        for handler in handlers:
            if handler.phase in self._handlers:
                raise ValueError(f"Multiple handlers registered for phase {handler.phase}")
            self._handlers[handler.phase] = handler

    def get(self, phase: SimulationPhase) -> BasePhaseHandler:
        try:
            return self._handlers[phase]
        except KeyError as exc:
            raise KeyError(f"No handler registered for phase {phase}") from exc

    def phases(self) -> List[SimulationPhase]:  # pragma: no cover - trivial
        return list(self._handlers.keys())


class InitializePhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.INITIALIZE

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        if simulation.status == SimulationStatus.CREATED:
            simulation.start()
            notes.append("Simulation started")
        elif simulation.status == SimulationStatus.PAUSED:
            simulation.resume()
            notes.append("Simulation resumed from paused state")

        simulation.current_phase = SimulationPhase.INITIALIZE
        simulation.updated_at = datetime.utcnow()
        notes.append("Initialization phase complete")

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.EVENT_GENERATION,
            notes=notes,
        )


class EventGenerationPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.EVENT_GENERATION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []
        generated_event_ids: List[str] = []
        generated_action_ids: List[str] = []

        scenario_service = context.scenario_service
        if scenario_service is None:
            notes.append(
                "No scenario service configured; skipping scenario-driven event generation."
            )
        else:
            scenario_key = simulation.scenario_module
            scenario = scenario_service.select(scenario_key)

            if scenario is None:
                notes.append(
                    f"Scenario '{scenario_key}' is not registered; skipping scenario seeding."
                )
            else:
                scenario_metadata = simulation.metadata.setdefault("scenario", {})
                seeded = bool(scenario_metadata.get("seeded"))

                if not seeded:
                    # First cycle: seed scenario
                    scenario_context = ScenarioContext(state=simulation)
                    scenario.seed(scenario_context)
                    scenario_metadata["seeded"] = True
                    scenario_metadata["seeded_at"] = datetime.utcnow().isoformat()

                    event_ids, action_ids = await self._persist_generated_entities(
                        context,
                        simulation,
                        scenario_context.actors,
                        scenario_context.events,
                        scenario_context.actions,
                    )
                    generated_event_ids.extend(event_ids)
                    generated_action_ids.extend(action_ids)
                    notes.append(
                        f"Seeded scenario '{scenario_key}': "
                        f"{len(scenario_context.actors)} actors, "
                        f"{len(scenario_context.events)} events, "
                        f"{len(scenario_context.actions)} actions."
                    )
                else:
                    # Subsequent cycles: use LLM to generate new events
                    new_events = await self._generate_events_with_llm(context)
                    if new_events:
                        event_ids, _ = await self._persist_generated_entities(
                            context, simulation, [], new_events, []
                        )
                        generated_event_ids.extend(event_ids)
                        notes.append(f"Generated {len(new_events)} new events via LLM.")
                    else:
                        notes.append("No new events generated this cycle.")

        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.ACTION_COLLECTION,
            notes=notes,
            generated_event_ids=generated_event_ids,
            generated_action_ids=generated_action_ids,
        )

    async def _generate_events_with_llm(self, context: PhaseContext) -> List[Event]:
        """Use LLM to generate new events based on current simulation state."""
        
        if not context.llm_service:
            logger.info("No LLM service available; skipping AI-driven event generation")
            return []
        
        simulation = context.simulation
        
        # Gather current state
        actors = await self._load_actors(context)
        events = await self._load_events(context)
        actions = await self._load_actions(context)
        
        # Build context for LLM
        sim_context = build_simulation_context(simulation, actors, events, actions)
        prompt = EVENT_GENERATION_PROMPT.format(context=sim_context)
        
        try:
            # Call LLM
            response = await context.llm_service.complete([
                LLMMessage(role="system", content="You are a creative narrative simulation engine."),
                LLMMessage(role="user", content=prompt)
            ])
            
            # Parse response
            events_data = parse_llm_json_response(response.content, expected_type="array")
            
            # Create Event objects
            new_events: List[Event] = []
            for event_data in events_data:
                try:
                    event = Event(
                        id=f"event-{uuid.uuid4().hex[:8]}",
                        title=safe_get_str(event_data, "title", "Untitled Event"),
                        description=safe_get_str(event_data, "description", ""),
                        type=EventType(event_data.get("type", "social")),
                        status=EventStatus.PENDING,
                        affected_actors=safe_get_list(event_data, "affected_actors"),
                        location=safe_get_dict(event_data, "location"),
                        scope=safe_get_str(event_data, "scope", "local"),
                        source=safe_get_str(event_data, "source", "AI-generated"),
                        trigger_action_id=event_data.get("trigger_action_id"),
                        parameters=safe_get_dict(event_data, "parameters"),
                        metadata=safe_get_dict(event_data, "metadata"),
                        scheduled_for=datetime.utcnow(),
                    )
                    new_events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to create event from LLM data: {e}")
                    continue
            
            logger.info(f"LLM generated {len(new_events)} events")
            return new_events
            
        except Exception as e:
            logger.error(f"Error generating events with LLM: {e}")
            return []
    
    async def _load_actors(self, context: PhaseContext) -> List[Actor]:
        """Load active actors from simulation."""
        actors: List[Actor] = []
        for actor_id in context.simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actors.append(actor)
        return actors
    
    async def _load_events(self, context: PhaseContext) -> List[Event]:
        """Load pending events from simulation."""
        events: List[Event] = []
        for event_id in context.simulation.pending_event_ids:
            event = await context.event_repository.get(event_id)
            if event:
                events.append(event)
        return events
    
    async def _load_actions(self, context: PhaseContext) -> List[Action]:
        """Load pending actions from simulation."""
        actions: List[Action] = []
        for action_id in context.simulation.pending_action_ids:
            action = await context.action_repository.get(action_id)
            if action:
                actions.append(action)
        return actions

    async def _build_context_from_state(self, context: PhaseContext) -> ScenarioContext:
        scenario_context = ScenarioContext(state=context.simulation)

        actors: List[Actor] = []
        for actor_id in context.simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actors.append(actor)

        events: List[Event] = []
        for event_id in context.simulation.pending_event_ids:
            event = await context.event_repository.get(event_id)
            if event:
                events.append(event)

        actions: List[Action] = []
        for action_id in context.simulation.pending_action_ids:
            action = await context.action_repository.get(action_id)
            if action:
                actions.append(action)

        scenario_context.extend(actors=actors, events=events, actions=actions)
        return scenario_context

    async def _persist_generated_entities(
        self,
        context: PhaseContext,
        simulation: SimulationState,
        new_actors: Sequence[Actor],
        new_events: Sequence[Event],
        new_actions: Sequence[Action],
    ) -> tuple[List[str], List[str]]:
        generated_event_ids: List[str] = []
        generated_action_ids: List[str] = []

        for actor in new_actors:
            exists = await context.actor_repository.exists(actor.id)
            if not exists:
                await context.actor_repository.create(actor)
            simulation.add_actor(actor.id)

        for event in new_events:
            exists = await context.event_repository.exists(event.id)
            if not exists:
                await context.event_repository.create(event)
            simulation.add_pending_event(event.id)
            generated_event_ids.append(event.id)

        for action in new_actions:
            # Ensure action has simulation_id set
            if not action.simulation_id:
                action.simulation_id = simulation.id
            
            exists = await context.action_repository.exists(action.id)
            if not exists:
                await context.action_repository.create(action)
            simulation.add_pending_action(action.id)
            generated_action_ids.append(action.id)

        return generated_event_ids, generated_action_ids


class ActionCollectionPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.ACTION_COLLECTION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        # Filter out completed/cancelled actions from the simulation's pending list
        # Don't pull ALL actions - only process the ones assigned to this simulation
        active_action_ids = []
        for action_id in simulation.pending_action_ids:
            action = await context.action_repository.get(action_id)
            if action and action.status not in {ActionStatus.COMPLETED, ActionStatus.CANCELLED}:
                active_action_ids.append(action_id)
        
        simulation.pending_action_ids = active_action_ids
        notes.append(
            f"Tracked {len(simulation.pending_action_ids)} pending actions for resolution."
        )
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.ACTION_RESOLUTION,
            notes=notes,
        )


class ActionResolutionPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.ACTION_RESOLUTION

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []
        generated_event_ids: List[str] = []

        if not simulation.pending_action_ids:
            notes.append("No actions queued for resolution.")
        else:
            # Resolve actions with LLM
            resolutions, new_events = await self._resolve_actions_with_llm(context)
            
            # Update action statuses
            for resolution in resolutions:
                action_id = resolution.get("action_id")
                if not action_id:
                    continue
                    
                action = await context.action_repository.get(action_id)
                if not action:
                    continue
                
                # Update action status
                outcome_desc = resolution.get("outcome_description", "Action resolved")
                new_status = resolution.get("status", "completed")
                if new_status == "completed":
                    action.complete(outcome=outcome_desc, success=True)
                elif new_status == "failed":
                    action.complete(outcome=outcome_desc, success=False)
                
                # Apply actor effects
                actor_effects = resolution.get("actor_effects", {})
                if actor_effects:
                    await self._apply_actor_effects(context, action.actor_id, actor_effects)
                
                await context.action_repository.update(action.id, action.to_dict())
            
            # Persist generated events
            if new_events:
                for event in new_events:
                    await context.event_repository.create(event)
                    simulation.add_pending_event(event.id)
                    generated_event_ids.append(event.id)
            
            notes.append(f"Resolved {len(resolutions)} actions, generated {len(new_events)} consequent events.")

        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.WORLD_UPDATE,
            notes=notes,
            generated_event_ids=generated_event_ids,
        )
    
    async def _resolve_actions_with_llm(self, context: PhaseContext) -> tuple[List[Dict], List[Event]]:
        """Use LLM to resolve pending actions and generate consequence events."""
        
        if not context.llm_service:
            logger.info("No LLM service available; auto-completing actions")
            # Fallback: just mark actions as completed
            resolutions = []
            for action_id in context.simulation.pending_action_ids:
                action = await context.action_repository.get(action_id)
                if action and action.status == ActionStatus.PENDING:
                    resolutions.append({
                        "action_id": action_id,
                        "status": "completed",
                        "outcome_description": "Action completed (no LLM available)",
                        "actor_effects": {},
                        "generated_events": []
                    })
            return resolutions, []
        
        simulation = context.simulation
        
        # Gather current state
        actors = []
        for actor_id in simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actors.append(actor)
        
        events = []
        for event_id in simulation.pending_event_ids:
            event = await context.event_repository.get(event_id)
            if event:
                events.append(event)
        
        actions = []
        for action_id in simulation.pending_action_ids:
            action = await context.action_repository.get(action_id)
            if action and action.status == ActionStatus.PENDING:
                actions.append(action)
        
        if not actions:
            return [], []
        
        # Build context for LLM
        sim_context = build_simulation_context(simulation, actors, events, actions)
        prompt = ACTION_RESOLUTION_PROMPT.format(context=sim_context)
        
        try:
            # Call LLM
            response = await context.llm_service.complete([
                LLMMessage(role="system", content="You are a realistic simulation resolution engine."),
                LLMMessage(role="user", content=prompt)
            ])
            
            # Parse response
            resolutions_data = parse_llm_json_response(response.content, expected_type="array")
            
            # Create Event objects from generated events
            new_events: List[Event] = []
            for resolution in resolutions_data:
                generated_events = resolution.get("generated_events", [])
                for event_data in generated_events:
                    try:
                        event = Event(
                            id=f"event-{uuid.uuid4().hex[:8]}",
                            title=safe_get_str(event_data, "title", "Action Consequence"),
                            description=safe_get_str(event_data, "description", ""),
                            type=EventType(event_data.get("type", "social")),
                            status=EventStatus.PENDING,
                            affected_actors=safe_get_list(event_data, "affected_actors"),
                            source=safe_get_str(event_data, "source", "action_resolution"),
                            trigger_action_id=resolution.get("action_id"),
                            scheduled_for=datetime.utcnow(),
                        )
                        new_events.append(event)
                    except Exception as e:
                        logger.warning(f"Failed to create event from resolution data: {e}")
            
            logger.info(f"LLM resolved {len(resolutions_data)} actions")
            return resolutions_data, new_events
            
        except Exception as e:
            logger.error(f"Error resolving actions with LLM: {e}")
            # Fallback: mark actions as completed
            fallback_resolutions = []
            for action in actions:
                fallback_resolutions.append({
                    "action_id": action.id,
                    "status": "completed",
                    "outcome_description": f"Action completed (LLM error: {str(e)[:100]})",
                    "actor_effects": {},
                    "generated_events": []
                })
            return fallback_resolutions, []
    
    async def _apply_actor_effects(self, context: PhaseContext, actor_id: str, effects: Dict[str, Any]) -> None:
        """Apply effects to an actor from action resolution."""
        actor = await context.actor_repository.get(actor_id)
        if not actor:
            return
        
        # Apply attribute changes
        attribute_changes = effects.get("attribute_changes", {})
        if attribute_changes:
            for key, value in attribute_changes.items():
                # Handle nested attributes like "traits.leadership"
                if "." in key:
                    parts = key.split(".")
                    current = actor.attributes
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    actor.attributes[key] = value
        
        # Apply location change
        location_change = effects.get("location_change")
        if location_change:
            actor.location = location_change
        
        # Apply metadata updates
        metadata_updates = effects.get("metadata_updates", {})
        if metadata_updates:
            actor.metadata.update(metadata_updates)
        
        await context.actor_repository.update(actor_id, actor.to_dict())


class WorldUpdatePhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.WORLD_UPDATE

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        if not simulation.pending_event_ids:
            notes.append("No pending events to apply to world state.")
        else:
            # Apply event effects with LLM
            updates = await self._apply_world_updates_with_llm(context)
            
            # Apply actor updates
            actor_updates = updates.get("actor_updates", [])
            for update in actor_updates:
                actor_id = update.get("actor_id")
                if not actor_id:
                    continue
                
                actor = await context.actor_repository.get(actor_id)
                if not actor:
                    continue
                
                # Apply attribute changes
                attribute_changes = update.get("attribute_changes", {})
                if attribute_changes:
                    for key, value in attribute_changes.items():
                        if "." in key:
                            parts = key.split(".")
                            current = actor.attributes
                            for part in parts[:-1]:
                                if part not in current:
                                    current[part] = {}
                                current = current[part]
                            current[parts[-1]] = value
                        else:
                            actor.attributes[key] = value
                
                # Apply location change
                location_change = update.get("location_change")
                if location_change:
                    actor.location = location_change
                
                # Apply metadata updates
                metadata_updates = update.get("metadata_updates", {})
                if metadata_updates:
                    actor.metadata.update(metadata_updates)
                
                await context.actor_repository.update(actor_id, actor.to_dict())
            
            # Update world state
            world_changes = updates.get("world_state_changes", {})
            if world_changes:
                simulation.metadata.setdefault("world_state", {}).update(world_changes)
            
            # Mark events as resolved
            for event_id in simulation.pending_event_ids:
                event = await context.event_repository.get(event_id)
                if event:
                    event.resolve()
                    await context.event_repository.update(event_id, event.to_dict())
            
            notes.append(f"Applied effects of {len(simulation.pending_event_ids)} events to {len(actor_updates)} actors.")
        
        # Clear pending events after processing
        simulation.pending_event_ids = []
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.SNAPSHOT,
            notes=notes,
        )
    
    async def _apply_world_updates_with_llm(self, context: PhaseContext) -> Dict[str, Any]:
        """Use LLM to determine how events affect actors and the world."""
        
        if not context.llm_service:
            logger.info("No LLM service available; skipping AI-driven world updates")
            return {"actor_updates": [], "world_state_changes": {}}
        
        simulation = context.simulation
        
        # Gather current state
        actors = []
        for actor_id in simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actors.append(actor)
        
        events = []
        for event_id in simulation.pending_event_ids:
            event = await context.event_repository.get(event_id)
            if event:
                events.append(event)
        
        if not events:
            return {"actor_updates": [], "world_state_changes": {}}
        
        # Build context for LLM
        sim_context = build_simulation_context(simulation, actors, events, [])
        prompt = WORLD_UPDATE_PROMPT.format(context=sim_context)
        
        try:
            # Call LLM
            response = await context.llm_service.complete([
                LLMMessage(role="system", content="You are a simulation world state manager."),
                LLMMessage(role="user", content=prompt)
            ])
            
            # Parse response
            updates = parse_llm_json_response(response.content, expected_type="object")
            
            logger.info(f"LLM generated world updates for {len(events)} events")
            return updates
            
        except Exception as e:
            logger.error(f"Error applying world updates with LLM: {e}")
            return {"actor_updates": [], "world_state_changes": {}}


class SnapshotPhaseHandler(BasePhaseHandler):
    phase = SimulationPhase.SNAPSHOT

    async def run(self, context: PhaseContext) -> PhaseResult:
        simulation = context.simulation
        notes: List[str] = []

        # Record comprehensive snapshot
        snapshot_data = await self._create_snapshot(context)
        simulation.record_snapshot()
        simulation.metadata.setdefault("snapshots", []).append({
            "cycle": simulation.phase_number,
            "timestamp": datetime.utcnow().isoformat(),
            "actor_count": len(simulation.active_actor_ids),
            "pending_events": len(simulation.pending_event_ids),
            "pending_actions": len(simulation.pending_action_ids),
            "summary": snapshot_data.get("summary", "")
        })
        
        notes.append(f"Snapshot recorded for cycle {simulation.phase_number}.")
        notes.append(f"Actors: {len(simulation.active_actor_ids)}, Events: {len(simulation.pending_event_ids)}, Actions: {len(simulation.pending_action_ids)}")
        simulation.updated_at = datetime.utcnow()

        return PhaseResult(
            simulation=simulation,
            executed_phase=self.phase,
            next_phase=SimulationPhase.EVENT_GENERATION,
            notes=notes,
        )
    
    async def _create_snapshot(self, context: PhaseContext) -> Dict[str, Any]:
        """Create a comprehensive snapshot of the current simulation state."""
        simulation = context.simulation
        
        # Gather actor states
        actor_snapshots = []
        for actor_id in simulation.active_actor_ids:
            actor = await context.actor_repository.get(actor_id)
            if actor:
                actor_snapshots.append({
                    "id": actor.id,
                    "name": actor.name,
                    "location": actor.location,
                    "attributes": actor.attributes,
                })
        
        return {
            "cycle": simulation.phase_number,
            "status": simulation.status.value,
            "actors": actor_snapshots,
            "summary": f"Cycle {simulation.phase_number} complete"
        }
