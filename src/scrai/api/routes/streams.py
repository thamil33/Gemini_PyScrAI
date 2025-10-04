"""Server-Sent Events endpoints for simulation updates."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from ..dependencies import get_runtime_manager
from ..schemas import SimulationStreamEvent
from .simulations import build_simulation_detail, build_simulation_summary

router = APIRouter(prefix="/streams", tags=["streams"])

_HEARTBEAT_SECONDS = 15


@router.get("/simulations/{simulation_id}")
async def stream_simulation(simulation_id: str) -> EventSourceResponse:
    """Stream simulation updates using Server-Sent Events."""

    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()

    simulation = await runtime.simulation_repository.get(simulation_id)
    if simulation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation {simulation_id} not found",
        )

    subscriber_queue = await runtime_manager.subscribe_to_stream(simulation_id)

    detail = await build_simulation_detail(runtime, simulation)
    summary = build_simulation_summary(simulation)
    initial_event = SimulationStreamEvent(
        event="simulation.snapshot",
        simulation_id=simulation_id,
        ts=datetime.now(timezone.utc),
        detail=detail,
        summary=summary,
    )
    await subscriber_queue.put(initial_event.model_dump(mode="json"))

    async def event_generator():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(
                        subscriber_queue.get(),
                        timeout=_HEARTBEAT_SECONDS,
                    )
                except asyncio.TimeoutError:
                    heartbeat_payload = {
                        "event": "heartbeat",
                        "simulation_id": simulation_id,
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                    yield {
                        "event": "heartbeat",
                        "data": json.dumps(heartbeat_payload),
                    }
                    continue

                yield {
                    "event": event.get("event", "message"),
                    "data": json.dumps(event),
                }
        except asyncio.CancelledError:  # pragma: no cover - server shutdown
            raise
        finally:
            await runtime_manager.unsubscribe_from_stream(
                simulation_id,
                subscriber_queue,
            )

    headers = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return EventSourceResponse(event_generator(), headers=headers)
