"""
Event model representing occurrences in the simulation.

An Event represents something that happens in the simulation world,
affecting actors, the environment, or the simulation state.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Types of events in the simulation."""
    ENVIRONMENTAL = "environmental"
    SOCIAL = "social" 
    ECONOMIC = "economic"
    POLITICAL = "political"
    SYSTEM = "system"
    PLAYER_ACTION = "player_action"
    NPC_ACTION = "npc_action"


class EventStatus(str, Enum):
    """Status of events in the simulation."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class Event(BaseModel):
    """
    Represents an event in the simulation.
    
    An event is something that happens in the simulation world,
    potentially affecting actors, the environment, or the simulation state.
    """
    
    id: str = Field(..., description="Unique identifier for the event")
    title: str = Field(..., description="Brief title of the event")
    description: str = Field(..., description="Detailed description of the event")
    type: EventType = Field(..., description="Type/category of the event")
    status: EventStatus = Field(default=EventStatus.PENDING, description="Current status")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_for: Optional[datetime] = Field(default=None, description="When event should occur")
    resolved_at: Optional[datetime] = Field(default=None, description="When event was resolved")
    
    # Scope and effects
    affected_actors: List[str] = Field(
        default_factory=list,
        description="IDs of actors affected by this event"
    )
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Location where event occurs"
    )
    scope: str = Field(default="local", description="Scope of event (local, regional, global)")
    
    # Event data
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific parameters and data"
    )
    effects: Dict[str, Any] = Field(
        default_factory=dict,
        description="Effects this event will have on the world/actors"
    )
    
    # Origin and causality
    source: str = Field(default="system", description="What generated this event")
    trigger_event_id: Optional[str] = Field(default=None, description="Event that triggered this one")
    trigger_action_id: Optional[str] = Field(default=None, description="Action that triggered this one")
    
    # Researcher mediation
    requires_approval: bool = Field(default=False, description="Whether event needs researcher approval")
    approved_by: Optional[str] = Field(default=None, description="Researcher who approved event")
    modifications: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Modifications made by researchers"
    )
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    def confirm(self, approved_by: Optional[str] = None) -> None:
        """Confirm the event, optionally with researcher approval."""
        self.status = EventStatus.CONFIRMED
        if approved_by:
            self.approved_by = approved_by
    
    def resolve(self) -> None:
        """Mark event as resolved."""
        self.status = EventStatus.RESOLVED
        self.resolved_at = datetime.utcnow()
    
    def cancel(self, reason: str = "") -> None:
        """Cancel the event."""
        self.status = EventStatus.CANCELLED
        if reason:
            self.metadata["cancellation_reason"] = reason
    
    def add_affected_actor(self, actor_id: str) -> None:
        """Add an actor to the affected list."""
        if actor_id not in self.affected_actors:
            self.affected_actors.append(actor_id)
    
    def add_modification(self, field: str, old_value: Any, new_value: Any, modified_by: str) -> None:
        """Record a modification made by a researcher."""
        modification = {
            "field": field,
            "old_value": old_value,
            "new_value": new_value,
            "modified_by": modified_by,
            "modified_at": datetime.utcnow().isoformat()
        }
        self.modifications.append(modification)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage."""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        return f"Event({self.title}, {self.type.value}, {self.status.value})"
    
    def __repr__(self) -> str:
        return f"Event(id='{self.id}', title='{self.title}', type='{self.type.value}', status='{self.status.value}')"