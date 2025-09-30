"""
Action repository for ScrAI data persistence.

This module provides the Action-specific repository implementation
with Firestore backend and action-specific query methods.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.action import Action, ActionType, ActionStatus, ActionPriority
from .repository import Repository, RepositoryError
from .firestore_client import FirestoreClient

logger = logging.getLogger(__name__)


class ActionRepository(Repository[Action]):
    """
    Repository for Action entities with Firestore backend.
    
    Provides CRUD operations and action-specific queries like
    finding actions by status, actor, or priority.
    """
    
    COLLECTION_NAME = "actions"
    
    def __init__(self, firestore_client: FirestoreClient):
        """Initialize the Action repository."""
        self.firestore_client = firestore_client
    
    async def create(self, action: Action) -> str:
        """Create a new action in Firestore."""
        try:
            await self.firestore_client.create_document(
                self.COLLECTION_NAME, 
                action.id, 
                action.to_dict()
            )
            logger.info(f"Created action: {action.id} by {action.actor_id}")
            return action.id
        except Exception as e:
            logger.error(f"Failed to create action {action.id}: {e}")
            raise RepositoryError(f"Failed to create action: {e}", "create", "Action", action.id)
    
    async def get(self, action_id: str) -> Optional[Action]:
        """Retrieve an action by ID."""
        try:
            data = await self.firestore_client.get_document(self.COLLECTION_NAME, action_id)
            if data:
                return Action.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get action {action_id}: {e}")
            raise RepositoryError(f"Failed to get action: {e}", "get", "Action", action_id)
    
    async def update(self, action_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing action."""
        try:
            result = await self.firestore_client.update_document(
                self.COLLECTION_NAME, 
                action_id, 
                updates
            )
            
            if result:
                logger.info(f"Updated action: {action_id}")
            else:
                logger.warning(f"Action not found for update: {action_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to update action {action_id}: {e}")
            raise RepositoryError(f"Failed to update action: {e}", "update", "Action", action_id)
    
    async def delete(self, action_id: str) -> bool:
        """Delete an action by ID."""
        try:
            result = await self.firestore_client.delete_document(self.COLLECTION_NAME, action_id)
            
            if result:
                logger.info(f"Deleted action: {action_id}")
            else:
                logger.warning(f"Action not found for deletion: {action_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to delete action {action_id}: {e}")
            raise RepositoryError(f"Failed to delete action: {e}", "delete", "Action", action_id)
    
    async def list_all(self, limit: Optional[int] = None) -> List[Action]:
        """List all actions."""
        try:
            documents = await self.firestore_client.list_documents(self.COLLECTION_NAME, limit)
            actions = [Action.from_dict(doc) for doc in documents]
            logger.debug(f"Listed {len(actions)} actions")
            return actions
        except Exception as e:
            logger.error(f"Failed to list actions: {e}")
            raise RepositoryError(f"Failed to list actions: {e}", "list", "Action")
    
    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[Action]:
        """Query actions with filters."""
        try:
            documents = await self.firestore_client.query_documents(
                self.COLLECTION_NAME, 
                filters, 
                limit
            )
            actions = [Action.from_dict(doc) for doc in documents]
            logger.debug(f"Queried {len(actions)} actions with filters {filters}")
            return actions
        except Exception as e:
            logger.error(f"Failed to query actions: {e}")
            raise RepositoryError(f"Failed to query actions: {e}", "query", "Action")
    
    async def exists(self, action_id: str) -> bool:
        """Check if an action exists."""
        try:
            return await self.firestore_client.document_exists(self.COLLECTION_NAME, action_id)
        except Exception as e:
            logger.error(f"Failed to check action existence {action_id}: {e}")
            raise RepositoryError(f"Failed to check action existence: {e}", "exists", "Action", action_id)
    
    # Action-specific methods
    
    async def find_by_actor(self, actor_id: str, limit: Optional[int] = None) -> List[Action]:
        """Find actions by actor."""
        return await self.query({"actor_id": actor_id}, limit)
    
    async def find_by_status(self, status: ActionStatus, limit: Optional[int] = None) -> List[Action]:
        """Find actions by status."""
        return await self.query({"status": status.value}, limit)
    
    async def find_by_type(self, action_type: ActionType, limit: Optional[int] = None) -> List[Action]:
        """Find actions by type."""
        return await self.query({"type": action_type.value}, limit)
    
    async def find_by_priority(self, priority: ActionPriority, limit: Optional[int] = None) -> List[Action]:
        """Find actions by priority."""
        return await self.query({"priority": priority.value}, limit)
    
    async def find_pending_approval(self, limit: Optional[int] = None) -> List[Action]:
        """Find actions requiring approval."""
        return await self.query({"requires_approval": True, "status": ActionStatus.PENDING.value}, limit)
    
    async def find_pending_execution(self, limit: Optional[int] = None) -> List[Action]:
        """Find actions ready for execution."""
        return await self.query({"status": ActionStatus.APPROVED.value}, limit)
    
    async def find_active(self, limit: Optional[int] = None) -> List[Action]:
        """Find currently executing actions."""
        return await self.query({"status": ActionStatus.EXECUTING.value}, limit)