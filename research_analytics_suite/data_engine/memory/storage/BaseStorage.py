"""
Base Storage Module

This module defines the abstract base class for storage backends for memory slot collections.

Author: Lane
"""
import uuid
from abc import ABC, abstractmethod

from research_analytics_suite.utils.Config import Config
from research_analytics_suite.utils.CustomLogger import CustomLogger


class BaseStorage(ABC):
    """
    Abstract base class for storage backends.
    """
    _GENERAL_MEMORY_ID = None

    def __init__(self, *args, **kwargs):
        self._GENERAL_MEMORY_ID = f"{uuid.uuid4()}"
        self._logger = CustomLogger()
        self._config = Config()

        from research_analytics_suite.data_engine.Workspace import Workspace
        self._workspace = Workspace()

        self.db_path = kwargs.get('db_path', None)

    @abstractmethod
    async def setup(self):  # pragma: no cover
        """
        Sets up the storage backend.
        """
        pass

    @abstractmethod
    async def add_collection(self, collection) -> str:  # pragma: no cover
        """
        Adds a new MemorySlotCollection to the storage.

        Args:
            collection (MemorySlotCollection): The collection to add.

        Returns:
            str: The ID of the added collection.
        """
        pass

    @abstractmethod
    async def get_collection(self, collection_id: str):     # pragma: no cover
        """
        Retrieves a MemorySlotCollection by its ID from the storage.

        Args:
            collection_id (str): The ID of the collection to retrieve.

        Returns:
            MemorySlotCollection: The retrieved collection.
        """
        pass

    @abstractmethod
    async def remove_collection(self, collection_id: str):  # pragma: no cover
        """
        Removes a MemorySlotCollection by its ID from the storage.

        Args:
            collection_id (str): The ID of the collection to remove.
        """
        pass

    @abstractmethod
    async def list_collections(self) -> dict:   # pragma: no cover
        """
        Lists all MemorySlotCollections from the storage.

        Returns:
            dict: A dictionary of MemorySlotCollections.
        """
        pass
