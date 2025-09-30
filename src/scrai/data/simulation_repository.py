"""
Simulation repository for ScrAI data persistence.

This module provides the SimulationState-specific repository implementation
with Firestore backend and simulation-specific query methods.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.simulation_state import SimulationState, SimulationStatus, SimulationPhase
from .repository import Repository, RepositoryError
from .firestore_client import FirestoreClient

logger = logging.getLogger(__name__)


class SimulationRepository(Repository[SimulationState]):
    """
    Repository for SimulationState entities with Firestore backend.
    
    Provides CRUD operations and simulation-specific queries like
    finding simulations by status or scenario module.
    """
    
    COLLECTION_NAME = "simulations"
    
    def __init__(self, firestore_client: FirestoreClient):
        """Initialize the Simulation repository."""
        self.firestore_client = firestore_client
    
    async def create(self, simulation: SimulationState) -> str:
        """Create a new simulation in Firestore."""
        try:
            await self.firestore_client.create_document(
                self.COLLECTION_NAME, 
                simulation.id, 
                simulation.to_dict()
            )
            logger.info(f"Created simulation: {simulation.id} ({simulation.name})")
            return simulation.id
        except Exception as e:
            logger.error(f"Failed to create simulation {simulation.id}: {e}")
            raise RepositoryError(f"Failed to create simulation: {e}", "create", "SimulationState", simulation.id)
    
    async def get(self, simulation_id: str) -> Optional[SimulationState]:
        """Retrieve a simulation by ID."""
        try:
            data = await self.firestore_client.get_document(self.COLLECTION_NAME, simulation_id)
            if data:
                return SimulationState.from_dict(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get simulation {simulation_id}: {e}")
            raise RepositoryError(f"Failed to get simulation: {e}", "get", "SimulationState", simulation_id)
    
    async def update(self, simulation_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing simulation."""
        try:
            result = await self.firestore_client.update_document(
                self.COLLECTION_NAME, 
                simulation_id, 
                updates
            )
            
            if result:
                logger.info(f"Updated simulation: {simulation_id}")
            else:
                logger.warning(f"Simulation not found for update: {simulation_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to update simulation {simulation_id}: {e}")
            raise RepositoryError(f"Failed to update simulation: {e}", "update", "SimulationState", simulation_id)
    
    async def delete(self, simulation_id: str) -> bool:
        """Delete a simulation by ID."""
        try:
            result = await self.firestore_client.delete_document(self.COLLECTION_NAME, simulation_id)
            
            if result:
                logger.info(f"Deleted simulation: {simulation_id}")
            else:
                logger.warning(f"Simulation not found for deletion: {simulation_id}")
            
            return result
        except Exception as e:
            logger.error(f"Failed to delete simulation {simulation_id}: {e}")
            raise RepositoryError(f"Failed to delete simulation: {e}", "delete", "SimulationState", simulation_id)
    
    async def list_all(self, limit: Optional[int] = None) -> List[SimulationState]:
        """List all simulations."""
        try:
            documents = await self.firestore_client.list_documents(self.COLLECTION_NAME, limit)
            simulations = [SimulationState.from_dict(doc) for doc in documents]
            logger.debug(f"Listed {len(simulations)} simulations")
            return simulations
        except Exception as e:
            logger.error(f"Failed to list simulations: {e}")
            raise RepositoryError(f"Failed to list simulations: {e}", "list", "SimulationState")
    
    async def query(self, filters: Dict[str, Any], limit: Optional[int] = None) -> List[SimulationState]:
        """Query simulations with filters."""
        try:
            documents = await self.firestore_client.query_documents(
                self.COLLECTION_NAME, 
                filters, 
                limit
            )
            simulations = [SimulationState.from_dict(doc) for doc in documents]
            logger.debug(f"Queried {len(simulations)} simulations with filters {filters}")
            return simulations
        except Exception as e:
            logger.error(f"Failed to query simulations: {e}")
            raise RepositoryError(f"Failed to query simulations: {e}", "query", "SimulationState")
    
    async def exists(self, simulation_id: str) -> bool:
        """Check if a simulation exists."""
        try:
            return await self.firestore_client.document_exists(self.COLLECTION_NAME, simulation_id)
        except Exception as e:
            logger.error(f"Failed to check simulation existence {simulation_id}: {e}")
            raise RepositoryError(f"Failed to check simulation existence: {e}", "exists", "SimulationState", simulation_id)
    
    # Simulation-specific methods
    
    async def find_by_status(self, status: SimulationStatus, limit: Optional[int] = None) -> List[SimulationState]:
        """Find simulations by status."""
        return await self.query({"status": status.value}, limit)
    
    async def find_by_scenario(self, scenario_module: str, limit: Optional[int] = None) -> List[SimulationState]:
        """Find simulations by scenario module."""
        return await self.query({"scenario_module": scenario_module}, limit)
    
    async def find_running(self, limit: Optional[int] = None) -> List[SimulationState]:
        """Find currently running simulations."""
        return await self.find_by_status(SimulationStatus.RUNNING, limit)
    
    async def find_completed(self, limit: Optional[int] = None) -> List[SimulationState]:
        """Find completed simulations."""
        return await self.find_by_status(SimulationStatus.COMPLETED, limit)
    
    async def find_by_name(self, name: str) -> Optional[SimulationState]:
        """Find simulation by exact name match."""
        simulations = await self.query({"name": name}, limit=1)
        return simulations[0] if simulations else None