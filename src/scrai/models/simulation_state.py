"""
SimulationState model representing the overall state of the simulation.

This model tracks the current state of the entire simulation including
phase information, global parameters, and metadata.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class SimulationPhase(str, Enum):
    """Phases of the simulation cycle."""
    INITIALIZE = "initialize"
    EVENT_GENERATION = "event_generation"
    ACTION_COLLECTION = "action_collection"
    ACTION_RESOLUTION = "action_resolution"
    WORLD_UPDATE = "world_update"
    SNAPSHOT = "snapshot"
    PAUSED = "paused"
    COMPLETED = "completed"


class SimulationStatus(str, Enum):
    """Overall status of the simulation."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class SimulationState(BaseModel):
    """
    Represents the overall state of a simulation.
    
    This model tracks the current state of the entire simulation including
    phase information, global parameters, world state, and metadata.
    """
    
    id: str = Field(..., description="Unique identifier for the simulation")
    name: str = Field(..., description="Human-readable name for the simulation")
    description: str = Field(default="", description="Description of the simulation")
    
    # Status and phase tracking
    status: SimulationStatus = Field(default=SimulationStatus.CREATED)
    current_phase: SimulationPhase = Field(default=SimulationPhase.INITIALIZE)
    phase_number: int = Field(default=0, description="Current phase/turn number")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Configuration
    max_phases: int = Field(default=100, description="Maximum number of phases before auto-completion")
    scenario_module: str = Field(default="basic", description="Name of the scenario module")
    configuration: Dict[str, Any] = Field(
        default_factory=dict,
        description="Simulation configuration parameters"
    )
    
    # World state
    world_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Global world state variables"
    )
    environment: Dict[str, Any] = Field(
        default_factory=dict,
        description="Environmental parameters and state"
    )
    
    # Active collections
    active_actor_ids: List[str] = Field(
        default_factory=list,
        description="IDs of currently active actors"
    )
    pending_event_ids: List[str] = Field(
        default_factory=list,
        description="IDs of pending events"
    )
    pending_action_ids: List[str] = Field(
        default_factory=list,
        description="IDs of pending actions"
    )
    
    # Phase statistics
    phase_statistics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistics for each phase"
    )
    
    # Researcher settings
    auto_approve_events: bool = Field(default=False, description="Auto-approve LLM generated events")
    auto_approve_actions: bool = Field(default=False, description="Auto-approve parsed actions")
    researcher_mode: bool = Field(default=True, description="Enable researcher mediation")
    
    # Error handling
    last_error: Optional[str] = Field(default=None, description="Last error message")
    error_count: int = Field(default=0, description="Number of errors encountered")
    
    # Snapshots
    snapshot_count: int = Field(default=0, description="Number of snapshots taken")
    last_snapshot_at: Optional[datetime] = Field(default=None, description="When last snapshot was taken")
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional simulation metadata"
    )
    
    def start(self) -> None:
        """Start the simulation."""
        self.status = SimulationStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def pause(self) -> None:
        """Pause the simulation."""
        self.status = SimulationStatus.PAUSED
        self.current_phase = SimulationPhase.PAUSED
        self.updated_at = datetime.utcnow()
    
    def resume(self) -> None:
        """Resume a paused simulation."""
        if self.status == SimulationStatus.PAUSED:
            self.status = SimulationStatus.RUNNING
            # Resume from the phase we were in before pausing
            self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """Mark the simulation as completed."""
        self.status = SimulationStatus.COMPLETED
        self.current_phase = SimulationPhase.COMPLETED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def advance_phase(self, next_phase: SimulationPhase) -> None:
        """Advance to the next phase."""
        if next_phase == SimulationPhase.INITIALIZE:
            self.phase_number += 1
        
        self.current_phase = next_phase
        self.updated_at = datetime.utcnow()
        
        # Check if we've reached max phases
        if self.phase_number >= self.max_phases:
            self.complete()
    
    def record_error(self, error_message: str) -> None:
        """Record an error in the simulation."""
        self.last_error = error_message
        self.error_count += 1
        self.status = SimulationStatus.ERROR
        self.updated_at = datetime.utcnow()
    
    def clear_error(self) -> None:
        """Clear the error state."""
        if self.status == SimulationStatus.ERROR:
            self.last_error = None
            self.status = SimulationStatus.RUNNING
            self.updated_at = datetime.utcnow()
    
    def add_actor(self, actor_id: str) -> None:
        """Add an actor to the simulation."""
        if actor_id not in self.active_actor_ids:
            self.active_actor_ids.append(actor_id)
            self.updated_at = datetime.utcnow()
    
    def remove_actor(self, actor_id: str) -> None:
        """Remove an actor from the simulation."""
        if actor_id in self.active_actor_ids:
            self.active_actor_ids.remove(actor_id)
            self.updated_at = datetime.utcnow()
    
    def add_pending_event(self, event_id: str) -> None:
        """Add a pending event."""
        if event_id not in self.pending_event_ids:
            self.pending_event_ids.append(event_id)
            self.updated_at = datetime.utcnow()
    
    def remove_pending_event(self, event_id: str) -> None:
        """Remove a pending event."""
        if event_id in self.pending_event_ids:
            self.pending_event_ids.remove(event_id)
            self.updated_at = datetime.utcnow()
    
    def add_pending_action(self, action_id: str) -> None:
        """Add a pending action."""
        if action_id not in self.pending_action_ids:
            self.pending_action_ids.append(action_id)
            self.updated_at = datetime.utcnow()
    
    def remove_pending_action(self, action_id: str) -> None:
        """Remove a pending action."""
        if action_id in self.pending_action_ids:
            self.pending_action_ids.remove(action_id)
            self.updated_at = datetime.utcnow()
    
    def record_snapshot(self) -> None:
        """Record that a snapshot was taken."""
        self.snapshot_count += 1
        self.last_snapshot_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_world_state(self, updates: Dict[str, Any]) -> None:
        """Update the world state."""
        self.world_state.update(updates)
        self.updated_at = datetime.utcnow()
    
    def update_phase_statistics(self, phase: str, stats: Dict[str, Any]) -> None:
        """Update statistics for a phase."""
        if phase not in self.phase_statistics:
            self.phase_statistics[phase] = {}
        
        self.phase_statistics[phase].update(stats)
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation state to dictionary for storage."""
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationState':
        """Create simulation state from dictionary."""
        return cls(**data)
    
    def __str__(self) -> str:
        return f"SimulationState({self.name}, {self.status.value}, Phase {self.phase_number})"
    
    def __repr__(self) -> str:
        return f"SimulationState(id='{self.id}', name='{self.name}', status='{self.status.value}', phase='{self.current_phase.value}')"