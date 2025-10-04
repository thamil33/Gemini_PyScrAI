"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SimulationCreateInput(BaseModel):
    """Input schema for creating a new simulation."""
    name: str = Field(..., min_length=1, max_length=200)
    scenario: str = Field(..., min_length=1, max_length=100)


class ActionCreateInput(BaseModel):
    """Input schema for injecting a new action into a simulation."""

    actor_id: str = Field(..., min_length=1, max_length=100)
    intent: str = Field(..., min_length=1)
    description: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AddActorInput(BaseModel):
    """Input schema for adding an actor to a simulation."""

    actor_id: str = Field(..., min_length=1, max_length=100)


class ActionSummary(BaseModel):
    """Summary representation of an action."""

    id: str
    actor_id: str
    intent: str
    description: str
    status: str
    priority: str
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EventSummary(BaseModel):
    """Summary representation of an event."""

    id: str
    title: str
    description: str
    status: str
    type: str
    created_at: datetime
    scheduled_for: Optional[datetime] = None


class PhaseLogEntry(BaseModel):
    """Entry describing a previously executed phase."""

    phase: str
    timestamp: Optional[str] = None
    notes: List[str] = Field(default_factory=list)


class SimulationSummary(BaseModel):
    """Summary view of a simulation for list endpoints."""
    id: str
    name: str
    status: str
    current_phase: str
    phase_number: int
    pending_action_count: int = 0
    pending_event_count: int = 0
    last_updated: Optional[datetime] = None


class SimulationDetail(BaseModel):
    """Detailed view of a simulation."""
    id: str
    name: str
    scenario: str
    status: str
    current_phase: str
    phase_number: int
    pending_action_count: int = 0
    pending_event_count: int = 0
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    phase_history: list[str] = Field(default_factory=list)
    phase_log: List[PhaseLogEntry] = Field(default_factory=list)
    actors: List[ActorSummary] = Field(default_factory=list)
    pending_actions: List[ActionSummary] = Field(default_factory=list)
    pending_events: List[EventSummary] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PhaseAdvanceResult(BaseModel):
    """Result of advancing a simulation phase."""
    simulation_id: str
    previous_phase: str
    current_phase: str
    phase_number: int
    status: str
    message: str


class SimulationStreamEvent(BaseModel):
    """Event envelope emitted over the simulation SSE stream."""

    event: str
    simulation_id: str
    ts: datetime
    detail: Optional[SimulationDetail] = None
    summary: Optional[SimulationSummary] = None
    phase_result: Optional[PhaseAdvanceResult] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error_type: str
    detail: str


class LLMStatusResponse(BaseModel):
    """Status payload for LLM health checks."""

    available: bool
    ready: bool
    providers: List[str] = Field(default_factory=list)
    detail: Optional[str] = None


class ActorCreateInput(BaseModel):
    """Input schema for creating a new actor."""

    name: str = Field(..., min_length=1, max_length=200)
    type: str = Field(..., min_length=1, max_length=50)
    attributes: Optional[Dict[str, Any]] = Field(default=None)
    location: Optional[Dict[str, Any]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ActorUpdateInput(BaseModel):
    """Input schema for updating an existing actor."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    active: Optional[bool] = Field(default=None)
    attributes: Optional[Dict[str, Any]] = Field(default=None)
    location: Optional[Dict[str, Any]] = Field(default=None)
    metadata: Optional[Dict[str, Any]] = Field(default=None)


class ActorSummary(BaseModel):
    """Summary representation of an actor."""

    id: str
    name: str
    type: str
    active: bool = True
    last_updated: Optional[datetime] = None


class ActorDetail(BaseModel):
    """Detailed view of an actor."""

    id: str
    name: str
    type: str
    active: bool = True
    attributes: Dict[str, Any] = Field(default_factory=dict)
    location: Optional[Dict[str, Any]] = Field(default=None)
    visibility: Dict[str, Any] = Field(default_factory=dict)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    affiliations: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
