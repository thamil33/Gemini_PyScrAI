"""
Abstract repository interface for ScrAI data persistence.

This module defines the base repository interface that all concrete
implementations must follow, enabling flexible backend switching.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


class Repository(ABC, Generic[T]):
    """
    Abstract base class for all repositories.
    
    Defines the standard CRUD interface that all concrete repository
    implementations must provide. This abstraction allows swapping
    between different persistence backends (Firestore, PostgreSQL, etc.)
    """
    
    @abstractmethod
    async def create(self, entity: T) -> str:
        """
        Create a new entity.
        
        Args:
            entity: The entity to create
            
        Returns:
            str: The ID of the created entity
            
        Raises:
            RepositoryError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get(self, entity_id: str) -> Optional[T]:
        """
        Retrieve an entity by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            Optional[T]: The entity if found, None otherwise
            
        Raises:
            RepositoryError: If retrieval fails
        """
        pass
    
    @abstractmethod
    async def update(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing entity.
        
        Args:
            entity_id: Unique identifier for the entity
            updates: Dictionary of field updates
            
        Returns:
            bool: True if update succeeded, False if entity not found
            
        Raises:
            RepositoryError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            bool: True if deletion succeeded, False if entity not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None) -> List[T]:
        """
        List all entities of this type.
        
        Args:
            limit: Optional limit on number of results
            
        Returns:
            List[T]: List of entities
            
        Raises:
            RepositoryError: If listing fails
        """
        pass
    
    @abstractmethod
    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[T]:
        """
        Query entities with filters.
        
        Args:
            filters: Dictionary of field filters
            limit: Optional limit on number of results
            
        Returns:
            List[T]: List of matching entities
            
        Raises:
            RepositoryError: If query fails
        """
        pass
    
    @abstractmethod
    async def exists(self, entity_id: str) -> bool:
        """
        Check if an entity exists.
        
        Args:
            entity_id: Unique identifier for the entity
            
        Returns:
            bool: True if entity exists, False otherwise
            
        Raises:
            RepositoryError: If check fails
        """
        pass


class RepositoryError(Exception):
    """Exception raised for repository operation failures."""
    
    def __init__(self, message: str, operation: str = "", entity_type: str = "", entity_id: str = ""):
        self.message = message
        self.operation = operation
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(self.message)
    
    def __str__(self) -> str:
        context = f" ({self.operation} on {self.entity_type}:{self.entity_id})" if self.operation else ""
        return f"{self.message}{context}"