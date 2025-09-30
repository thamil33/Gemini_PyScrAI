"""
Actor model representing entities in the simulation.

An Actor represents any entity that can perform actions or be affected by events
in the simulation world. This includes players, NPCs, organizations, and other
dynamic entities.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ActorType(str, Enum):
    """Types of actors in the simulation."""
    PLAYER = "player"
    NPC = "npc"
    ORGANIZATION = "organization"
    ENTITY = "entity"


class Actor(BaseModel):
    """
    Represents an actor in the simulation.
    
    An actor is any entity that can perform actions or be affected by events.
    This includes players, NPCs, organizations, and other dynamic entities.
    """
    
    id: str = Field(..., description="Unique identifier for the actor")
    name: str = Field(..., description="Display name of the actor")
    type: ActorType = Field(..., description="Type of actor (player, NPC, etc.)")
    
    # Core attributes
    attributes: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic attributes (health, stats, properties, etc.)"
    )
    
    # Location and visibility
    location: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Current location (coordinates, region, etc.)"
    )
    visibility: Dict[str, Any] = Field(
        default_factory=dict,
        description="What this actor can see/know about"
    )
    
    # Relationships and affiliations
    relationships: Dict[str, Any] = Field(
        default_factory=dict,
        description="Relationships with other actors"
    )
    affiliations: List[str] = Field(
        default_factory=list,
        description="Groups or organizations this actor belongs to"
    )
    
    # State tracking
    active: bool = Field(default=True, description="Whether the actor is active in simulation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the actor"
    )
    
    def update_attributes(self, updates: Dict[str, Any]) -> None:
        """Update actor attributes."""
        self.attributes.update(updates)
        self.updated_at = datetime.utcnow()
    
    def set_location(self, location: Dict[str, Any]) -> None:
        """Update actor location."""
        self.location = location
        self.updated_at = datetime.utcnow()
    
    def add_relationship(self, actor_id: str, relationship: str, strength: float = 1.0) -> None:
        """Add or update a relationship with another actor."""
        if "relationships" not in self.relationships:
            self.relationships["relationships"] = {}
        
        self.relationships["relationships"][actor_id] = {
            "type": relationship,
            "strength": strength,
            "established": datetime.utcnow().isoformat()
        }
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert actor to dictionary for storage."""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Actor':
        """Create actor from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        return f"Actor({self.name}, {self.type.value})"
    
    def __repr__(self) -> str:
        return f"Actor(id='{self.id}', name='{self.name}', type='{self.type.value}')"