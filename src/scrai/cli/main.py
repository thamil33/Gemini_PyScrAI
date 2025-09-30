from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

import click

from ..engine.context import PhaseResult
from ..models import Action, Actor, Event, SimulationState
from ..models.action import ActionPriority, ActionType
from ..models.simulation_state import SimulationPhase
from ..models.actor import ActorType
from .runtime import RuntimeContext, build_runtime
from .store import DEFAULT_STATE_PATH


def _run(coro):
    return asyncio.run(coro)


def _ensure_simulation(runtime: RuntimeContext, simulation_id: str) -> SimulationState:
    simulation = _run(runtime.simulation_repository.get(simulation_id))
    if simulation is None:
        raise click.ClickException(f"Simulation '{simulation_id}' not found.")
    return simulation


def _format_datetime(value: Optional[datetime]) -> str:
    return value.isoformat() if isinstance(value, datetime) else str(value) if value else "-"


def _print_simulation(simulation: SimulationState, *, compact: bool = False) -> None:
    click.echo(f"ID: {simulation.id}")
    click.echo(f"Name: {simulation.name}")
    click.echo(f"Status: {simulation.status.value}")
    click.echo(f"Current Phase: {simulation.current_phase.value}")
    click.echo(f"Phase Number: {simulation.phase_number}")
    click.echo(f"Scenario: {simulation.scenario_module}")
    click.echo(f"Created: {_format_datetime(simulation.created_at)}")
    click.echo(f"Updated: {_format_datetime(simulation.updated_at)}")
    if compact:
        return
    click.echo("Pending Actions: " + ", ".join(simulation.pending_action_ids) or "None")
    click.echo("Pending Events: " + ", ".join(simulation.pending_event_ids) or "None")
    if simulation.metadata.get("phase_log"):
        click.echo("Phase Log Entries: " + str(len(simulation.metadata["phase_log"])))


def _print_phase_result(result: PhaseResult) -> None:
    click.echo(f"Executed Phase: {result.executed_phase.value}")
    click.echo(f"Next Phase: {result.next_phase.value}")
    if result.generated_event_ids:
        click.echo("Generated Events: " + ", ".join(result.generated_event_ids))
    if result.generated_action_ids:
        click.echo("Generated Actions: " + ", ".join(result.generated_action_ids))
    if result.notes:
        click.echo("Notes:")
        for note in result.notes:
            click.echo(f"  - {note}")


def _parse_metadata(pairs: tuple[str, ...]) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.ClickException(f"Invalid metadata entry '{pair}'. Use key=value format.")
        key, value = pair.split("=", 1)
        metadata[key.strip()] = value.strip()
    return metadata


def _load_or_create_actor(
    runtime: RuntimeContext,
    *,
    actor_id: str,
    name: Optional[str] = None,
    actor_type: ActorType = ActorType.NPC,
    auto_create: bool = False,
) -> Actor:
    actor = _run(runtime.actor_repository.get(actor_id))
    if actor:
        return actor
    if not auto_create:
        raise click.ClickException(
            f"Actor '{actor_id}' not found. Use --auto-create-actor to create a lightweight actor."
        )
    actor = Actor(
        id=actor_id,
        name=name or actor_id,
        type=actor_type,
    )
    _run(runtime.actor_repository.create(actor))
    return actor


@click.group()
@click.option("--backend", type=click.Choice(["memory", "firestore"]), default="memory")
@click.option(
    "--state-path",
    type=click.Path(path_type=Path),
    default=DEFAULT_STATE_PATH,
    help="Location for CLI state when using the memory backend.",
)
@click.option("--project-id", type=str, default=None, help="Firestore project ID.")
@click.option("--credentials", type=click.Path(path_type=Path), default=None, help="Path to Firestore credentials JSON.")
@click.version_option()
@click.pass_context
def cli(ctx: click.Context, backend: str, state_path: Path, project_id: Optional[str], credentials: Optional[Path]) -> None:
    """ScrAI command-line interface for simulation control."""

    runtime = build_runtime(
        backend=backend,
        state_path=state_path,
        project_id=project_id,
        credentials_path=str(credentials) if credentials else None,
    )
    ctx.obj = runtime
    if backend == "memory":
        click.echo(f"Using memory backend (state file: {runtime.state_path})", err=True)
    else:
        click.echo("Using Firestore backend", err=True)


def main() -> None:  # pragma: no cover - console entrypoint
    cli(auto_envvar_prefix="SCRAI")


def _phase_from_string(value: Optional[str]) -> Optional[SimulationPhase]:
    if value is None:
        return None
    try:
        return SimulationPhase(value)
    except ValueError as exc:
        valid = ", ".join(p.value for p in SimulationPhase)
        raise click.ClickException(f"Invalid phase '{value}'. Expected one of: {valid}") from exc


@cli.group()
@click.pass_obj
def simulation(runtime: RuntimeContext) -> None:
    """Simulation management commands."""


@simulation.command("create")
@click.option("--name", required=True)
@click.option("--description", default="")
@click.option("--scenario", default="simple_town")
@click.option("--max-phases", type=int, default=20)
@click.option("--auto-approve-events", is_flag=True, default=False)
@click.option("--auto-approve-actions", is_flag=True, default=False)
@click.option("--researcher-mode/--no-researcher-mode", default=True)
@click.pass_obj
def simulation_create(
    runtime: RuntimeContext,
    name: str,
    description: str,
    scenario: str,
    max_phases: int,
    auto_approve_events: bool,
    auto_approve_actions: bool,
    researcher_mode: bool,
) -> None:
    simulation_id = f"sim-{uuid4().hex[:8]}"
    simulation = SimulationState(
        id=simulation_id,
        name=name,
        description=description,
        scenario_module=scenario,
        max_phases=max_phases,
        auto_approve_events=auto_approve_events,
        auto_approve_actions=auto_approve_actions,
        researcher_mode=researcher_mode,
    )
    _run(runtime.simulation_repository.create(simulation))
    click.echo(f"Created simulation {simulation_id}")


@simulation.command("list")
@click.pass_obj
def simulation_list(runtime: RuntimeContext) -> None:
    simulations = _run(runtime.simulation_repository.list_all())
    if not simulations:
        click.echo("No simulations found.")
        return
    for simulation in simulations:
        click.echo("-" * 40)
        _print_simulation(simulation, compact=True)
    click.echo("-" * 40)


@simulation.command("show")
@click.argument("simulation_id")
@click.option("--details", is_flag=True, default=False, help="Show actors, events, and actions")
@click.pass_obj
def simulation_show(runtime: RuntimeContext, simulation_id: str, details: bool) -> None:
    simulation = _ensure_simulation(runtime, simulation_id)
    _print_simulation(simulation)

    if not details:
        return

    actors = _run(runtime.actor_repository.list_all())
    click.echo("\nActors:")
    for actor in actors:
        click.echo(f"  - {actor.id}: {actor.name} [{actor.type.value}]")

    events = _run(runtime.event_repository.list_all())
    if events:
        click.echo("\nEvents:")
        for event in events:
            click.echo(f"  - {event.id}: {event.title} [{event.status.value}]")

    actions = _run(runtime.action_repository.list_all())
    if actions:
        click.echo("\nActions:")
        for action in actions:
            click.echo(f"  - {action.id}: {action.intent} [{action.status.value}]")


@simulation.command("start")
@click.argument("simulation_id")
@click.pass_obj
def simulation_start(runtime: RuntimeContext, simulation_id: str) -> None:
    simulation = _ensure_simulation(runtime, simulation_id)
    if simulation.status.value not in {"created", "paused"}:
        click.echo(f"Simulation is already {simulation.status.value}.")
        return
    result = _run(runtime.phase_engine.step(simulation_id))
    _print_phase_result(result)


@simulation.command("advance")
@click.argument("simulation_id")
@click.option("--phase", type=str, default=None)
@click.pass_obj
def simulation_advance(runtime: RuntimeContext, simulation_id: str, phase: Optional[str]) -> None:
    force_phase = _phase_from_string(phase)
    result = _run(runtime.phase_engine.step(simulation_id, force_phase=force_phase))
    _print_phase_result(result)


@simulation.command("cycle")
@click.argument("simulation_id")
@click.pass_obj
def simulation_cycle(runtime: RuntimeContext, simulation_id: str) -> None:
    results = _run(runtime.phase_engine.run_cycle(simulation_id))
    for result in results:
        click.echo("-" * 40)
        _print_phase_result(result)
    if not results:
        click.echo("No phases executed (simulation may be in a terminal state).")


@simulation.command("log")
@click.argument("simulation_id")
@click.pass_obj
def simulation_log(runtime: RuntimeContext, simulation_id: str) -> None:
    simulation = _ensure_simulation(runtime, simulation_id)
    phase_log = simulation.metadata.get("phase_log", [])
    if not phase_log:
        click.echo("No phase log entries recorded.")
        return
    for entry in phase_log:
        click.echo(f"[{entry.get('timestamp', '-')}] {entry.get('phase')} -> {entry.get('notes')}")


@cli.group()
@click.pass_obj
def action(runtime: RuntimeContext) -> None:
    """Action management commands."""


@action.command("inject")
@click.argument("simulation_id")
@click.option("--actor-id", required=True)
@click.option("--intent", required=True)
@click.option("--description", default=None)
@click.option("--action-type", type=click.Choice([t.value for t in ActionType]), default=ActionType.CUSTOM.value)
@click.option("--priority", type=click.Choice([p.value for p in ActionPriority]), default=ActionPriority.NORMAL.value)
@click.option("--event", "event_id", default=None)
@click.option("--metadata", multiple=True, help="Attach metadata key=value pairs")
@click.option("--auto-create-actor", is_flag=True, default=False)
@click.pass_obj
def action_inject(
    runtime: RuntimeContext,
    simulation_id: str,
    actor_id: str,
    intent: str,
    description: Optional[str],
    action_type: str,
    priority: str,
    event_id: Optional[str],
    metadata: tuple[str, ...],
    auto_create_actor: bool,
) -> None:
    simulation = _ensure_simulation(runtime, simulation_id)
    actor = _load_or_create_actor(runtime, actor_id=actor_id, auto_create=auto_create_actor)
    details = _parse_metadata(metadata)
    if event_id:
        details.setdefault("related_event", event_id)

    action_id = f"act-{uuid4().hex[:10]}"
    action = Action(
        id=action_id,
        actor_id=actor.id,
        type=ActionType(action_type),
        intent=intent,
        description=description or intent,
        priority=ActionPriority(priority),
        metadata=details,
    )
    _run(runtime.action_repository.create(action))
    simulation.add_pending_action(action_id)
    _run(runtime.simulation_repository.update(simulation_id, simulation.to_dict()))
    click.echo(f"Injected action {action_id} for simulation {simulation_id}")


@action.command("list")
@click.argument("simulation_id")
@click.pass_obj
def action_list(runtime: RuntimeContext, simulation_id: str) -> None:
    _ensure_simulation(runtime, simulation_id)
    actions = _run(runtime.action_repository.list_all())
    if not actions:
        click.echo("No actions recorded.")
        return
    for action in actions:
        click.echo(f"- {action.id}: {action.intent} [{action.status.value}] actor={action.actor_id}")


__all__ = ["cli", "main"]
