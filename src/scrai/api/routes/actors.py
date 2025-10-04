"""Actor management endpoints."""

from __future__ import annotations

from typing import Any, Dict, List
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from ..dependencies import get_runtime_manager
from ..schemas import (
    ActorCreateInput,
    ActorUpdateInput,
    ActorDetail,
    ActorSummary,
)
from ...models import Actor
from ...models.actor import ActorType

router = APIRouter(prefix="/actors", tags=["actors"])


async def _load_actor_or_404(runtime, actor_id: str) -> Actor:
    actor = await runtime.actor_repository.get(actor_id)
    if actor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor {actor_id} not found",
        )
    return actor


def build_actor_summary(actor: Actor) -> ActorSummary:
    """Construct an ActorSummary from the actor model."""
    return ActorSummary(
        id=actor.id,
        name=actor.name,
        type=actor.type.value,
        active=actor.active,
        last_updated=actor.updated_at,
    )


def build_actor_detail(actor: Actor) -> ActorDetail:
    """Construct an ActorDetail from the actor model."""
    return ActorDetail(
        id=actor.id,
        name=actor.name,
        type=actor.type.value,
        active=actor.active,
        attributes=actor.attributes,
        location=actor.location,
        visibility=actor.visibility,
        relationships=actor.relationships,
        affiliations=actor.affiliations,
        created_at=actor.created_at,
        last_updated=actor.updated_at,
        metadata=actor.metadata,
    )


@router.post("", response_model=ActorDetail, status_code=status.HTTP_201_CREATED)
async def create_actor(input_data: ActorCreateInput) -> ActorDetail:
    """Create a new actor."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()

    # Generate unique ID
    actor_id = f"actor-{uuid.uuid4().hex[:8]}"

    # Create actor
    actor = Actor(
        id=actor_id,
        name=input_data.name,
        type=ActorType(input_data.type),
        attributes=input_data.attributes or {},
        location=input_data.location,
        metadata=input_data.metadata or {},
    )

    # Save to repository
    await runtime.actor_repository.create(actor)

    return build_actor_detail(actor)


@router.get("", response_model=List[ActorSummary])
async def list_actors() -> List[ActorSummary]:
    """List all actors."""
    runtime = get_runtime_manager().get_runtime()

    actors = await runtime.actor_repository.list_all()

    return [build_actor_summary(actor) for actor in actors]


@router.get("/{actor_id}", response_model=ActorDetail)
async def get_actor(actor_id: str) -> ActorDetail:
    """Get actor details."""
    runtime = get_runtime_manager().get_runtime()

    actor = await _load_actor_or_404(runtime, actor_id)

    return build_actor_detail(actor)


@router.put("/{actor_id}", response_model=ActorDetail)
async def update_actor(actor_id: str, input_data: ActorUpdateInput) -> ActorDetail:
    """Update an existing actor."""
    runtime_manager = get_runtime_manager()
    runtime = runtime_manager.get_runtime()

    actor = await _load_actor_or_404(runtime, actor_id)

    # Apply updates
    updates = {}

    if input_data.name is not None:
        updates["name"] = input_data.name

    if input_data.type is not None:
        updates["type"] = ActorType(input_data.type).value

    if input_data.active is not None:
        updates["active"] = input_data.active

    if input_data.attributes is not None:
        updates["attributes"] = input_data.attributes

    if input_data.location is not None:
        updates["location"] = input_data.location

    if input_data.metadata is not None:
        updates["metadata"] = input_data.metadata

    # Update in repository
    await runtime.actor_repository.update(actor_id, updates)

    # Reload updated actor
    updated_actor = await runtime.actor_repository.get(actor_id)
    if updated_actor is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Actor disappeared after update",
        )

    return build_actor_detail(updated_actor)


@router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_actor(actor_id: str) -> None:
    """Delete an actor."""
    runtime = get_runtime_manager().get_runtime()

    # Check if actor exists
    actor = await runtime.actor_repository.get(actor_id)
    if actor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor {actor_id} not found",
        )

    # Delete from repository
    deleted = await runtime.actor_repository.delete(actor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete actor",
        )
