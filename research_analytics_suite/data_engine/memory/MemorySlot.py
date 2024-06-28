import builtins
import sys
import time
import asyncio
import types
from typing import Any, Type, Tuple, Dict


class MemorySlot:
    """
    A class representing a slot of memory for storing data associated with operations.

    Properties:
        memory_id (str): A unique identifier for the memory slot.
        name (str): A name for the memory slot.
        operation_required (bool): Indicates whether the operation requires this memory slot to function.
        data (dict): A dictionary to store key-value pairs where each value is a tuple (data_type, data_value).
        metadata (dict): A dictionary to store additional metadata.
        created_at (float): The timestamp of when the memory slot was created.
        modified_at (float): The timestamp of when the memory slot was last modified.

    Methods:
        get_data_by_key(key: str): Retrieve the value associated with a specific key.
        set_data_by_key(key: str, value: Any, data_type: Type): Set the value for a specific key.
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
    def __init__(self, memory_id: str, name: str, operation_required: bool, data: Dict[str, tuple[type, Any]]):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            operation_required (bool): Indicates whether the operation requires this memory slot to function.
            data (Dict[str, Tuple[Type, Any]]): A dictionary to store key-value pairs representing the data in the memory slot.
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
        return self._data

    @property
    def preview_data(self) -> Dict[str, Tuple[Type, str]]:
        """Get a data dictionary with the data value replaced by size as a formatted string."""
        def format_size(size_in_bytes: int) -> str:
            """Convert size from bytes to a human-readable string."""
            for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024:
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024
            return f"{size_in_bytes:.2f} PB"  # For completeness, although unlikely to reach PB.

        return {key: (data_type, format_size(sys.getsizeof(value))) for key, (data_type, value) in self._data.items()}

    def data_length(self) -> int:
        return sys.getsizeof(self._data)

    @data.setter
    async def data(self, value: Dict[str, Tuple[Type, Any]]):
        """Set the data dictionary."""
        if not isinstance(value, dict):
            raise ValueError("data must be a dictionary")
        for k, (t, v) in value.items():
            if not isinstance(k, str):
                raise ValueError("All keys in data must be strings")
            if not isinstance(v, t):
                raise ValueError(f"Value for key '{k}' must be of type {t}")
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
        if not isinstance(self._data.values(), tuple):
            values = list(self._data.values())
            _types = [type(v) for v in values]
            self._data = {k: (t, v) for k, t, v in zip(self._data.keys(), _types, values)}

        for k, (t, v) in self._data.items():
            if not isinstance(k, str):
                raise ValueError("All keys in data must be strings")
            if not isinstance(v, t):
                raise ValueError(f"Value for key '{k}' must be of type {t}")

    async def get_data_by_key(self, key: str) -> Any:
        """Retrieve the value associated with a specific key."""
        async with self._lock:
            return self._data.get(key, (None, None))[1]

    async def get_data_type_by_key(self, key: str) -> Type:
        """Retrieve the data type associated with a specific key."""
        async with self._lock:
            return self._data.get(key, (None, None))[0]

    async def set_data_by_key(self, key: str, value: Any, data_type: Type):
        """Set the value for a specific key."""
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not isinstance(value, data_type):
            raise ValueError(f"value must be of type {data_type}")
        async with self._lock:
            self._data[key] = (data_type, value)
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

    async def update_data(self, data: Dict[str, Tuple[Type, Any]]):
        """Update multiple key-value pairs in the data dictionary."""
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        for k, (t, v) in data.items():
            if not isinstance(k, str):
                raise ValueError("All keys in data must be strings")
            if not isinstance(v, t):
                raise ValueError(f"Value for key '{k}' must be of type {t}")
        async with self._lock:
            self._data.update(data)
            self.update_modified_time()

    async def merge_data(self, data: Dict[str, Tuple[Type, Any]]):
        """Merge another dictionary into the data dictionary."""
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        for k, (t, v) in data.items():
            if not isinstance(k, str):
                raise ValueError("All keys in data must be strings")
            if not isinstance(v, t):
                raise ValueError(f"Value for key '{k}' must be of type {t}")
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
            return [v for t, v in self._data.values()]

    async def data_items(self) -> list:
        """Return a list of key-value pairs in the data dictionary."""
        async with self._lock:
            return [(k, v) for k, (t, v) in self._data.items()]

    async def to_dict(self) -> dict:
        """Convert the MemorySlot instance to a dictionary."""
        async with self._lock:
            _data = dict()
            for k, v in self._data.items():
                if isinstance(v, tuple):
                    if v[0] is not type(None):
                        _data[k] = (v[0].__name__, v[1])
                else:
                    _data[k] = v
            return {
                'memory_id': self._memory_id,
                'name': self._name,
                'operation_required': self._operation_required,
                'data': _data,
                'metadata': self._metadata,
                'created_at': self._created_at,
                'modified_at': self._modified_at
            }

    @staticmethod
    async def load_from_disk(data: dict) -> 'MemorySlot':
        """Initialize a MemorySlot instance from a dictionary."""
        slot_data = data.get('data', {})
        for k, v in slot_data.items():
            print(v)
            _type = getattr(builtins, v[0])
            print(_type)
            slot_data[k] = (_type, v[1])
        print(slot_data)

        slot = MemorySlot(
            memory_id=data.get('memory_id', ''),
            name=data.get('name', ''),
            operation_required=data.get('operation_required', False),
            data=slot_data
        )
        slot._metadata = data.get('metadata', {})
        slot._created_at = data.get('created_at', time.time())
        slot._modified_at = data.get('modified_at', slot._created_at)
        return slot
