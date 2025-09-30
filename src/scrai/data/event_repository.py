"""
Event repository for ScrAI data persistence.

This module provides the Event-specific repository implementation
with Firestore backend and event-specific query methods.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.event import Event, EventType, EventStatus
from .repository import Repository, RepositoryError
from .firestore_client import FirestoreClient

logger = logging.getLogger(__name__)


class EventRepository(Repository[Event]):
    """
    Repository for Event entities with Firestore backend.
    
    Provides CRUD operations and event-specific queries like
    finding events by status, type, or affected actors.
    """
    
    COLLECTION_NAME = "events"
    
    def __init__(self, firestore_client: FirestoreClient):
        """Initialize the Event repository."""
        self.firestore_client = firestore_client
    
    async def create(self, event: Event) -> str:
        """Create a new event in Firestore."""
        try:
            await self.firestore_client.create_document(
                self.COLLECTION_NAME, 
                event.id, 
                event.to_dict()
            )
            logger.info(f"Created event: {event.id} ({event.title})")
            return event.id
        except Exception as e:
            logger.error(f"Failed to create event {event.id}: {e}")
            raise RepositoryError(f"Failed to create event: {e}", "create", "Event", event.id)
    
    async def get(self, event_id: str) -> Optional[Event]:
        """Retrieve an event by ID."""
        try:
            data = await self.firestore_client.get_document(self.COLLECTION_NAME, event_id)
            if data:
                return Event.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get event {event_id}: {e}")
            raise RepositoryError(f"Failed to get event: {e}", "get", "Event", event_id)
    
    async def update(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing event."""
        try:
            result = await self.firestore_client.update_document(
                self.COLLECTION_NAME, 
                event_id, 
                updates
            )
            
            if result:
                logger.info(f"Updated event: {event_id}")
            else:
                logger.warning(f"Event not found for update: {event_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to update event {event_id}: {e}")
            raise RepositoryError(f"Failed to update event: {e}", "update", "Event", event_id)
    
    async def delete(self, event_id: str) -> bool:
        """Delete an event by ID."""
        try:
            result = await self.firestore_client.delete_document(self.COLLECTION_NAME, event_id)
            
            if result:
                logger.info(f"Deleted event: {event_id}")
            else:
                logger.warning(f"Event not found for deletion: {event_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to delete event {event_id}: {e}")
            raise RepositoryError(f"Failed to delete event: {e}", "delete", "Event", event_id)
    
    async def list_all(self, limit: Optional[int] = None) -> List[Event]:
        """List all events."""
        try:
            documents = await self.firestore_client.list_documents(self.COLLECTION_NAME, limit)
            events = [Event.from_dict(doc) for doc in documents]
            logger.debug(f"Listed {len(events)} events")
            return events
        except Exception as e:
            logger.error(f"Failed to list events: {e}")
            raise RepositoryError(f"Failed to list events: {e}", "list", "Event")
    
    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Event]:
        """Query events with filters."""
        try:
            documents = await self.firestore_client.query_documents(
                self.COLLECTION_NAME, 
                filters, 
                limit
            )
            events = [Event.from_dict(doc) for doc in documents]
            logger.debug(f"Queried {len(events)} events with filters {filters}")
            return events
        except Exception as e:
            logger.error(f"Failed to query events: {e}")
            raise RepositoryError(f"Failed to query events: {e}", "query", "Event")
    
    async def exists(self, event_id: str) -> bool:
        """Check if an event exists."""
        try:
            return await self.firestore_client.document_exists(self.COLLECTION_NAME, event_id)
        except Exception as e:
            logger.error(f"Failed to check event existence {event_id}: {e}")
            raise RepositoryError(f"Failed to check event existence: {e}", "exists", "Event", event_id)
    
    # Event-specific methods
    
    async def find_by_status(self, status: EventStatus, limit: Optional[int] = None) -> List[Event]:
        """Find events by status."""
        return await self.query({"status": status.value}, limit)
    
    async def find_by_type(self, event_type: EventType, limit: Optional[int] = None) -> List[Event]:
        """Find events by type."""
        return await self.query({"type": event_type.value}, limit)
    
    async def find_pending_approval(self, limit: Optional[int] = None) -> List[Event]:
        """Find events requiring approval."""
        return await self.query({"requires_approval": True, "status": EventStatus.PENDING.value}, limit)
    
    async def find_by_actor(self, actor_id: str, limit: Optional[int] = None) -> List[Event]:
        """Find events affecting a specific actor."""
        # This requires array-contains query, which may not work in all Firestore setups
        # For now, fetch all and filter in memory
        try:
            all_events = await self.list_all()
            matching_events = []
            
            for event in all_events:
                if actor_id in event.affected_actors:
                    matching_events.append(event)
                    if limit and len(matching_events) >= limit:
                        break
            
            logger.debug(f"Found {len(matching_events)} events affecting actor {actor_id}")
            return matching_events
            
        except Exception as e:
            logger.error(f"Failed to find events by actor: {e}")
            raise RepositoryError(f"Failed to find events by actor: {e}", "query", "Event")
    
    async def find_recent(self, hours: int = 24, limit: Optional[int] = None) -> List[Event]:
        """Find events created within the last N hours."""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)
        
        # This would require a timestamp-based query in production
        # For now, fetch all and filter
        try:
            all_events = await self.list_all()
            recent_events = []
            
            for event in all_events:
                if event.created_at.timestamp() >= cutoff:
                    recent_events.append(event)
            
            # Sort by creation time, most recent first
            recent_events.sort(key=lambda e: e.created_at, reverse=True)
            
            if limit:
                recent_events = recent_events[:limit]
            
            logger.debug(f"Found {len(recent_events)} events from last {hours} hours")
            return recent_events
            
        except Exception as e:
            logger.error(f"Failed to find recent events: {e}")
            raise RepositoryError(f"Failed to find recent events: {e}", "query", "Event")