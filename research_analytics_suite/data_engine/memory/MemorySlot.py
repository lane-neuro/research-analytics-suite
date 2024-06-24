import time
import asyncio
from typing import Any


class MemorySlot:
    """
    A class representing a slot of memory for storing data associated with operations.

    Properties:
        memory_id (str): A unique identifier for the memory slot.
        name (str): A name for the memory slot.
        operation_required (bool): Indicates whether the operation requires this memory slot to function.
        data (dict): A dictionary to store key-value pairs representing the data in the memory slot.
        metadata (dict): A dictionary to store additional metadata.
        created_at (float): The timestamp of when the memory slot was created.
        modified_at (float): The timestamp of when the memory slot was last modified.

    Methods:
        get_data_by_key(key: str): Retrieve the value associated with a specific key.
        set_data_by_key(key: str, value): Set the value for a specific key.
        remove_data_by_key(key: str): Remove the key-value pair associated with a specific key.
        clear_data(): Clear all data in the data dictionary.
        has_key(key: str) -> bool: Check if a specific key exists in the data dictionary.
        update_data(data: dict): Update multiple key-value pairs in the data dictionary.
        merge_data(data: dict): Merge another dictionary into the data dictionary.
        data_keys() -> list: Return a list of keys in the data dictionary.
        data_values() -> list: Return a list of values in the data dictionary.
        data_items() -> list: Return a list of key-value pairs in the data dictionary.
        to_dict() -> dict: Convert the MemorySlot instance to a dictionary.
        from_dict(data: dict) -> 'MemorySlot': Initialize a MemorySlot instance from a dictionary.
    """
    def __init__(self, memory_id: str, name: str, operation_required: bool, data: dict):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            operation_required (bool): Indicates whether the operation requires this memory slot to function.
            data (dict): A dictionary to store key-value pairs representing the data in the memory slot.
        """
        self._memory_id = memory_id
        self._name = name
        self._operation_required = operation_required
        self._data = data
        self._metadata = {}
        self._created_at = time.time()
        self._modified_at = self._created_at
        self._lock = asyncio.Lock()
        self.validate_data()

    @property
    def memory_id(self) -> str:
        """Get the memory ID."""
        return self._memory_id

    @memory_id.setter
    async def memory_id(self, value: str):
        """Set the memory ID."""
        if not isinstance(value, str):
            raise ValueError("memory_id must be a string")
        async with self._lock:
            self._memory_id = value
            self.update_modified_time()

    @property
    def name(self) -> str:
        """Get the name of the memory slot."""
        return self._name

    @name.setter
    async def name(self, value: str):
        """Set the name of the memory slot."""
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        async with self._lock:
            self._name = value
            self.update_modified_time()

    @property
    def operation_required(self) -> bool:
        """Get whether the operation requires this memory slot to function."""
        return self._operation_required

    @operation_required.setter
    async def operation_required(self, value: bool):
        """Set whether the operation requires this memory slot to function."""
        if not isinstance(value, bool):
            raise ValueError("operation_required must be a boolean")
        async with self._lock:
            self._operation_required = value
            self.update_modified_time()

    @property
    def data(self):
        """Get the data dictionary."""
        return self._data.items()

    @data.setter
    async def data(self, value: dict):
        """Set the data dictionary."""
        if not isinstance(value, dict):
            raise ValueError("data must be a dictionary")
        async with self._lock:
            self._data = value
            self.update_modified_time()

    @property
    def metadata(self) -> dict:
        """Get the metadata dictionary."""
        return self._metadata

    @metadata.setter
    async def metadata(self, value: dict):
        """Set the metadata dictionary."""
        if not isinstance(value, dict):
            raise ValueError("metadata must be a dictionary")
        async with self._lock:
            self._metadata = value
            self.update_modified_time()

    @property
    def created_at(self) -> float:
        """Get the creation timestamp."""
        return self._created_at

    @property
    def modified_at(self) -> float:
        """Get the last modified timestamp."""
        return self._modified_at

    def update_modified_time(self):
        """Update the last modified timestamp."""
        self._modified_at = time.time()

    def validate_data(self):
        """Ensure that the data dictionary contains valid key-value pairs."""
        if not all(isinstance(k, str) for k in self._data.keys()):
            raise ValueError("All keys in data must be strings")

    async def get_data_by_key(self, key: str):
        """Retrieve the value associated with a specific key."""
        async with self._lock:
            return self._data.get(key, None)

    async def set_data_by_key(self, key: str, value):
        """Set the value for a specific key."""
        async with self._lock:
            self._data[key] = value
            self.update_modified_time()

    async def remove_data_by_key(self, key: str):
        """Remove the key-value pair associated with a specific key."""
        async with self._lock:
            if key in self._data:
                del self._data[key]
                self.update_modified_time()

    async def clear_data(self):
        """Clear all data in the data dictionary."""
        async with self._lock:
            self._data.clear()
            self.update_modified_time()

    async def has_key(self, key: str) -> bool:
        """Check if a specific key exists in the data dictionary."""
        async with self._lock:
            return key in self._data

    async def update_data(self, data: dict):
        """Update multiple key-value pairs in the data dictionary."""
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        async with self._lock:
            self._data.update(data)
            self.update_modified_time()

    async def merge_data(self, data: dict):
        """Merge another dictionary into the data dictionary."""
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        async with self._lock:
            self._data = {**self._data, **data}
            self.update_modified_time()

    async def data_keys(self) -> list:
        """Return a list of keys in the data dictionary."""
        async with self._lock:
            return list(self._data.keys())

    async def data_values(self) -> list:
        """Return a list of values in the data dictionary."""
        async with self._lock:
            return list(self._data.values())

    async def data_items(self) -> list:
        """Return a list of key-value pairs in the data dictionary."""
        async with self._lock:
            return list(self._data.items())

    async def to_dict(self) -> dict:
        """Convert the MemorySlot instance to a dictionary."""
        async with self._lock:
            return {
                'memory_id': self._memory_id,
                'name': self._name,
                'operation_required': self._operation_required,
                'data': self._data,
                'metadata': self._metadata,
                'created_at': self._created_at,
                'modified_at': self._modified_at
            }

    @staticmethod
    async def from_dict(data: dict) -> 'MemorySlot':
        """Initialize a MemorySlot instance from a dictionary."""
        slot = MemorySlot(
            memory_id=data.get('memory_id', ''),
            name=data.get('name', ''),
            operation_required=data.get('operation_required', False),
            data=data.get('data', {})
        )
        slot._metadata = data.get('metadata', {})
        slot._created_at = data.get('created_at', time.time())
        slot._modified_at = data.get('modified_at', slot._created_at)
        return slot
