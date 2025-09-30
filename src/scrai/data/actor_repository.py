"""
Actor repository for ScrAI data persistence.

This module provides the Actor-specific repository implementation
with Firestore backend and actor-specific query methods.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.actor import Actor, ActorType
from .repository import Repository, RepositoryError
from .firestore_client import FirestoreClient

logger = logging.getLogger(__name__)


class ActorRepository(Repository[Actor]):
    """
    Repository for Actor entities with Firestore backend.
    
    Provides CRUD operations and actor-specific queries like
    finding actors by type, location, or relationships.
    """
    
    COLLECTION_NAME = "actors"
    
    def __init__(self, firestore_client: FirestoreClient):
        """Initialize the Actor repository."""
        self.firestore_client = firestore_client
    
    async def create(self, actor: Actor) -> str:
        """Create a new actor in Firestore."""
        try:
            await self.firestore_client.create_document(
                self.COLLECTION_NAME, 
                actor.id, 
                actor.to_dict()
            )
            logger.info(f"Created actor: {actor.id} ({actor.name})")
            return actor.id
        except Exception as e:
            logger.error(f"Failed to create actor {actor.id}: {e}")
            raise RepositoryError(f"Failed to create actor: {e}", "create", "Actor", actor.id)
    
    async def get(self, actor_id: str) -> Optional[Actor]:
        """Retrieve an actor by ID."""
        try:
            data = await self.firestore_client.get_document(self.COLLECTION_NAME, actor_id)
            if data:
                return Actor.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get actor {actor_id}: {e}")
            raise RepositoryError(f"Failed to get actor: {e}", "get", "Actor", actor_id)
    
    async def update(self, actor_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing actor."""
        try:
            # Add updated_at timestamp
            updates['updated_at'] = datetime.utcnow()
            
            result = await self.firestore_client.update_document(
                self.COLLECTION_NAME, 
                actor_id, 
                updates
            )
            
            if result:
                logger.info(f"Updated actor: {actor_id}")
            else:
                logger.warning(f"Actor not found for update: {actor_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to update actor {actor_id}: {e}")
            raise RepositoryError(f"Failed to update actor: {e}", "update", "Actor", actor_id)
    
    async def delete(self, actor_id: str) -> bool:
        """Delete an actor by ID."""
        try:
            result = await self.firestore_client.delete_document(self.COLLECTION_NAME, actor_id)
            
            if result:
                logger.info(f"Deleted actor: {actor_id}")
            else:
                logger.warning(f"Actor not found for deletion: {actor_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to delete actor {actor_id}: {e}")
            raise RepositoryError(f"Failed to delete actor: {e}", "delete", "Actor", actor_id)
    
    async def list_all(self, limit: Optional[int] = None) -> List[Actor]:
        """List all actors."""
        try:
            documents = await self.firestore_client.list_documents(self.COLLECTION_NAME, limit)
            actors = [Actor.from_dict(doc) for doc in documents]
            logger.debug(f"Listed {len(actors)} actors")
            return actors
        except Exception as e:
            logger.error(f"Failed to list actors: {e}")
            raise RepositoryError(f"Failed to list actors: {e}", "list", "Actor")
    
    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Actor]:
        """Query actors with filters."""
        try:
            documents = await self.firestore_client.query_documents(
                self.COLLECTION_NAME, 
                filters, 
                limit
            )
            actors = [Actor.from_dict(doc) for doc in documents]
            logger.debug(f"Queried {len(actors)} actors with filters {filters}")
            return actors
        except Exception as e:
            logger.error(f"Failed to query actors: {e}")
            raise RepositoryError(f"Failed to query actors: {e}", "query", "Actor")
    
    async def exists(self, actor_id: str) -> bool:
        """Check if an actor exists."""
        try:
            return await self.firestore_client.document_exists(self.COLLECTION_NAME, actor_id)
        except Exception as e:
            logger.error(f"Failed to check actor existence {actor_id}: {e}")
            raise RepositoryError(f"Failed to check actor existence: {e}", "exists", "Actor", actor_id)
    
    # Actor-specific methods
    
    async def find_by_type(self, actor_type: ActorType, limit: Optional[int] = None) -> List[Actor]:
        """Find actors by type."""
        return await self.query({"type": actor_type.value}, limit)
    
    async def find_by_name(self, name: str) -> Optional[Actor]:
        """Find actor by exact name match."""
        actors = await self.query({"name": name}, limit=1)
        return actors[0] if actors else None
    
    async def find_active(self, limit: Optional[int] = None) -> List[Actor]:
        """Find all active actors."""
        return await self.query({"active": True}, limit)
    
    async def find_in_location(self, location_field: str, location_value: Any, limit: Optional[int] = None) -> List[Actor]:
        """
        Find actors in a specific location.
        
        Args:
            location_field: Field in location dict to filter on (e.g., "region", "coordinates.x")
            location_value: Value to match
            limit: Optional limit on results
        """
        # Note: Firestore has limitations on nested field queries
        # This is a simplified implementation
        try:
            all_actors = await self.list_all()
            matching_actors = []
            
            for actor in all_actors:
                if actor.location and self._check_location_match(actor.location, location_field, location_value):
                    matching_actors.append(actor)
                    if limit and len(matching_actors) >= limit:
                        break
            
            logger.debug(f"Found {len(matching_actors)} actors in location {location_field}={location_value}")
            return matching_actors
            
        except Exception as e:
            logger.error(f"Failed to find actors by location: {e}")
            raise RepositoryError(f"Failed to find actors by location: {e}", "query", "Actor")
    
    async def find_by_affiliation(self, affiliation: str, limit: Optional[int] = None) -> List[Actor]:
        """Find actors by affiliation."""
        # This requires a more complex query for array fields
        # For now, we'll fetch all and filter in memory
        try:
            all_actors = await self.list_all()
            matching_actors = []
            
            for actor in all_actors:
                if affiliation in actor.affiliations:
                    matching_actors.append(actor)
                    if limit and len(matching_actors) >= limit:
                        break
            
            logger.debug(f"Found {len(matching_actors)} actors with affiliation {affiliation}")
            return matching_actors
            
        except Exception as e:
            logger.error(f"Failed to find actors by affiliation: {e}")
            raise RepositoryError(f"Failed to find actors by affiliation: {e}", "query", "Actor")
    
    def _check_location_match(self, location: Dict[str, Any], field: str, value: Any) -> bool:
        """Helper to check if location matches the given field and value."""
        if "." in field:
            # Handle nested fields like "coordinates.x"
            parts = field.split(".")
            current = location
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return current == value
        else:
            # Simple field
            return location.get(field) == value