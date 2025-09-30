"""
Firestore client implementation for ScrAI data persistence.

This module provides the concrete Firestore implementation for data persistence,
handling connection management, error handling, and Firestore-specific operations.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

try:
    from google.cloud import firestore
    from google.cloud.firestore import AsyncClient
    from google.api_core import exceptions as firestore_exceptions
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    # Create a dummy type for type hints when Firestore is not available
    from typing import Any as AsyncClient

from .repository import RepositoryError

logger = logging.getLogger(__name__)


class FirestoreClient:
    """
    Firestore client for ScrAI data persistence.
    
    Handles connection management, batch operations, and Firestore-specific
    functionality. Provides a clean interface for repository implementations.
    """
    
    def __init__(self, project_id: Optional[str] = None, credentials_path: Optional[str] = None):
        """
        Initialize Firestore client.
        
        Args:
            project_id: Google Cloud project ID (optional if using default)
            credentials_path: Path to service account credentials JSON file
        """
        if not FIRESTORE_AVAILABLE:
            raise ImportError(
                "google-cloud-firestore is not installed. "
                "Install it with: pip install google-cloud-firestore"
            )
        
        self.project_id = project_id
        self.credentials_path = credentials_path
        self._client: Optional[AsyncClient] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Firestore client."""
        if self._initialized:
            return
        
        try:
            if self.credentials_path:
                # Use service account credentials
                import os
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
            
            self._client = firestore.AsyncClient(project=self.project_id)
            
            # Test connection
            await self._test_connection()
            
            self._initialized = True
            logger.info(f"Firestore client initialized for project: {self.project_id or 'default'}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise RepositoryError(f"Failed to initialize Firestore: {e}")
    
    async def _test_connection(self) -> None:
        """Test Firestore connection."""
        try:
            # Try to access collections (this will fail if no permissions/connection)
            collections = []
            async for collection in self._client.collections():
                collections.append(collection.id)
                break  # Just test that we can iterate
            logger.debug("Firestore connection test successful")
        except Exception as e:
            logger.warning(f"Firestore connection test failed: {e}")
            # Don't raise here as this might fail in emulator mode
    
    @property
    def client(self) -> AsyncClient:
        """Get the Firestore async client."""
        if not self._initialized or not self._client:
            raise RuntimeError("Firestore client not initialized. Call initialize() first.")
        return self._client
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> None:
        """
        Create a document in Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            data: Document data
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Add timestamp fields
            now = datetime.utcnow()
            data = data.copy()
            if 'created_at' not in data:
                data['created_at'] = now
            if 'updated_at' not in data:
                data['updated_at'] = now
            
            doc_ref = self.client.collection(collection).document(document_id)
            await doc_ref.set(data)
            
            logger.debug(f"Created document {collection}/{document_id}")
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error creating document: {e}")
            raise RepositoryError(f"Failed to create document: {e}", "create", collection, document_id)
        except Exception as e:
            logger.error(f"Unexpected error creating document: {e}")
            raise RepositoryError(f"Failed to create document: {e}", "create", collection, document_id)
    
    async def get_document(self, collection: str, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a document from Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            Optional[Dict[str, Any]]: Document data if found, None otherwise
            
        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            doc = await doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                # Add the document ID
                data['id'] = document_id
                logger.debug(f"Retrieved document {collection}/{document_id}")
                return data
            else:
                logger.debug(f"Document {collection}/{document_id} not found")
                return None
                
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error retrieving document: {e}")
            raise RepositoryError(f"Failed to retrieve document: {e}", "get", collection, document_id)
        except Exception as e:
            logger.error(f"Unexpected error retrieving document: {e}")
            raise RepositoryError(f"Failed to retrieve document: {e}", "get", collection, document_id)
    
    async def update_document(self, collection: str, document_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a document in Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            updates: Fields to update
            
        Returns:
            bool: True if update succeeded, False if document not found
            
        Raises:
            RepositoryError: If update fails
        """
        try:
            # Add updated timestamp
            updates = updates.copy()
            updates['updated_at'] = datetime.utcnow()
            
            doc_ref = self.client.collection(collection).document(document_id)
            
            # Check if document exists first
            doc = await doc_ref.get()
            if not doc.exists:
                logger.debug(f"Document {collection}/{document_id} not found for update")
                return False
            
            await doc_ref.update(updates)
            logger.debug(f"Updated document {collection}/{document_id}")
            return True
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error updating document: {e}")
            raise RepositoryError(f"Failed to update document: {e}", "update", collection, document_id)
        except Exception as e:
            logger.error(f"Unexpected error updating document: {e}")
            raise RepositoryError(f"Failed to update document: {e}", "update", collection, document_id)
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """
        Delete a document from Firestore.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            bool: True if deletion succeeded, False if document not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            
            # Check if document exists first
            doc = await doc_ref.get()
            if not doc.exists:
                logger.debug(f"Document {collection}/{document_id} not found for deletion")
                return False
            
            await doc_ref.delete()
            logger.debug(f"Deleted document {collection}/{document_id}")
            return True
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error deleting document: {e}")
            raise RepositoryError(f"Failed to delete document: {e}", "delete", collection, document_id)
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {e}")
            raise RepositoryError(f"Failed to delete document: {e}", "delete", collection, document_id)
    
    async def list_documents(self, collection: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all documents in a collection.
        
        Args:
            collection: Collection name
            limit: Optional limit on number of results
            
        Returns:
            List[Dict[str, Any]]: List of documents
            
        Raises:
            RepositoryError: If listing fails
        """
        try:
            query = self.client.collection(collection)
            if limit:
                query = query.limit(limit)
            
            documents = []
            async for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            logger.debug(f"Listed {len(documents)} documents from {collection}")
            return documents
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error listing documents: {e}")
            raise RepositoryError(f"Failed to list documents: {e}", "list", collection)
        except Exception as e:
            logger.error(f"Unexpected error listing documents: {e}")
            raise RepositoryError(f"Failed to list documents: {e}", "list", collection)
    
    async def query_documents(
        self, 
        collection: str, 
        filters: Dict[str, Any], 
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents with filters.
        
        Args:
            collection: Collection name
            filters: Dictionary of field filters (field: value)
            limit: Optional limit on number of results
            
        Returns:
            List[Dict[str, Any]]: List of matching documents
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            query = self.client.collection(collection)
            
            # Apply filters
            for field, value in filters.items():
                query = query.where(field, "==", value)
            
            if limit:
                query = query.limit(limit)
            
            documents = []
            async for doc in query.stream():
                data = doc.to_dict()
                data['id'] = doc.id
                documents.append(data)
            
            logger.debug(f"Queried {len(documents)} documents from {collection} with filters {filters}")
            return documents
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error querying documents: {e}")
            raise RepositoryError(f"Failed to query documents: {e}", "query", collection)
        except Exception as e:
            logger.error(f"Unexpected error querying documents: {e}")
            raise RepositoryError(f"Failed to query documents: {e}", "query", collection)
    
    async def document_exists(self, collection: str, document_id: str) -> bool:
        """
        Check if a document exists.
        
        Args:
            collection: Collection name
            document_id: Document ID
            
        Returns:
            bool: True if document exists, False otherwise
            
        Raises:
            RepositoryError: If check fails
        """
        try:
            doc_ref = self.client.collection(collection).document(document_id)
            doc = await doc_ref.get()
            exists = doc.exists
            
            logger.debug(f"Document {collection}/{document_id} exists: {exists}")
            return exists
            
        except firestore_exceptions.GoogleAPICallError as e:
            logger.error(f"Firestore API error checking document existence: {e}")
            raise RepositoryError(f"Failed to check document existence: {e}", "exists", collection, document_id)
        except Exception as e:
            logger.error(f"Unexpected error checking document existence: {e}")
            raise RepositoryError(f"Failed to check document existence: {e}", "exists", collection, document_id)
    
    async def close(self) -> None:
        """Close the Firestore client."""
        if self._client:
            # AsyncClient doesn't have an explicit close method
            self._client = None
        self._initialized = False
        logger.info("Firestore client closed")