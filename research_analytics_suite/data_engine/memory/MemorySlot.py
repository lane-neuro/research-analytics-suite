import builtins
import sys
import time
import asyncio
from mmap import mmap
from typing import Any, Type, Tuple, Dict

DATA_SIZE_THRESHOLD = 1024 * 1024  # 1 MB


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

    def __init__(self, memory_id: str, name: str, operation_required: bool, data: Dict[str, Tuple[Type, Any]],
                 file_path: str = None):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            operation_required (bool): Indicates whether the operation requires this memory slot to function.
            data (Dict[str, Tuple[Type, Any]]): A dictionary to store key-value pairs representing the data in
            the memory slot.
            file_path (str, optional): The file path for memory-mapped storage. Defaults to None.
        """
        self._memory_id = memory_id
        self._name = name
        self._operation_required = operation_required
        self._data = data
        self._metadata = {}
        self._created_at = time.time()
        self._modified_at = self._created_at
        self._lock = asyncio.Lock()

        self._use_mmap = False
        self._file_path = file_path
        self._mmapped_file = None
        self._file = None
        self._file_size = 0

        self.validate_data()
        self.check_data_size()

    def __del__(self):
        """Destructor to close the memory-mapped file."""
        self.close_mmap()

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
    def data(self) -> Dict[str, Tuple[Type, Any]]:
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

        return {key: (type(value), format_size(sys.getsizeof(value))) for key, (data_type, value) in self._data.items()}

    @property
    def data_length(self) -> int:
        """Get the size of the data dictionary in bytes."""
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
            self._data = dict(value.values())
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

    def check_data_size(self):
        """Check the data size and switch to mmap if necessary."""
        try:
            data_size = sum(sys.getsizeof(value) for _, value in self._data.values())
            if data_size > DATA_SIZE_THRESHOLD and self._file_path:
                self._use_mmap = True
                self._file_size = data_size
                self.init_mmap()
        except Exception as e:
            print(f"Error checking data size: {e}")

    def init_mmap(self):
        """Initialize the memory-mapped file."""
        try:
            if not self._file_path:
                raise ValueError("File path must be provided for memory mapping.")

            with open(self._file_path, 'wb') as f:
                f.write(b'\0' * self._file_size)

            self._file = open(self._file_path, 'r+b')
            self._mmapped_file = mmap(self._file.fileno(), self._file_size)

            self.dump_data_to_mmap()
        except Exception as e:
            print(f"Error initializing memory-mapped file: {e}")

    def dump_data_to_mmap(self):
        """Dump current data to the memory-mapped file."""
        try:
            offset = 0
            for key, (data_type, value) in self._data.items():
                serialized_value = self.serialize(value)
                size = len(serialized_value)
                self._mmapped_file[offset:offset+size] = serialized_value
                offset += size
        except Exception as e:
            print(f"Error dumping data to memory-mapped file: {e}")

    def serialize(self, value):
        """Serialize a value for storage in mmap."""
        try:
            return str(value).encode('utf-8')
        except Exception as e:
            print(f"Error serializing value: {e}")
            return b''

    def deserialize(self, value, data_type):
        """Deserialize a value from mmap."""
        try:
            return data_type(value.decode('utf-8'))
        except Exception as e:
            print(f"Error deserializing value: {e}")
            return None

    def close_mmap(self):
        """Close the memory-mapped file."""
        try:
            if self._mmapped_file:
                self._mmapped_file.close()
                self._file.close()
        except Exception as e:
            print(f"Error closing memory-mapped file: {e}")

    def update_modified_time(self):
        """Update the last modified timestamp."""
        self._modified_at = time.time()

    def validate_data(self):
        """Validate the data dictionary."""
        try:
            if not all(isinstance(v, tuple) for v in self._data.values()):
                values = list(self._data.values())
                if not values:
                    return

                _types = [type(v) for v in values[0]]
                self._data = {k: (t, v) for k, t, v in zip(self._data.keys(), _types, values)}

            for k, (t, v) in self._data.items():
                if not isinstance(k, str):
                    raise ValueError("All keys in data must be strings")
        except Exception as e:
            print(f"Error validating data: {e}")

    async def get_data_by_key(self, key: str) -> Any:
        """Retrieve the value associated with a specific key."""
        async with self._lock:
            try:
                if self._use_mmap:
                    return self.deserialize(self._mmapped_file[:], self._data[key][0])
                return self._data.get(key, (None, None))[1]
            except Exception as e:
                print(f"Error getting data by key '{key}': {e}")

    async def get_data_type_by_key(self, key: str) -> type:
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
            try:
                if key in self._data:
                    if self._use_mmap:
                        offset = self.calculate_offset(key)
                        size = len(self.serialize(self._data[key][1]))
                        self._mmapped_file[offset:offset+size] = b'\0' * size
                    del self._data[key]
                    self.update_modified_time()
            except Exception as e:
                print(f"Error removing data by key '{key}': {e}")

    async def clear_data(self):
        """Clear all data in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    self._mmapped_file[:] = b'\0' * self._file_size
                self._data.clear()
                self.update_modified_time()
            except Exception as e:
                print(f"Error clearing data: {e}")

    async def has_key(self, key: str) -> bool:
        """Check if a specific key exists in the data dictionary."""
        async with self._lock:
            return key in self._data

    def calculate_offset(self, key: str) -> int:
        """Calculate the offset for a key in the mmap file."""
        try:
            offset = 0
            for k in self._data.keys():
                if k == key:
                    break
                offset += len(self.serialize(self._data[k][1]))
            return offset
        except Exception as e:
            print(f"Error calculating offset for key '{key}': {e}")
            return 0

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
            try:
                if self._use_mmap:
                    for key, (data_type, value) in data.items():
                        await self.set_data_by_key(key, value, data_type)
                else:
                    self._data.update(data)
                self.update_modified_time()
            except Exception as e:
                print(f"Error updating data: {e}")

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
            try:
                if self._use_mmap:
                    for key, (data_type, value) in data.items():
                        await self.set_data_by_key(key, value, data_type)
                else:
                    self._data = {**self._data, **data}
                self.update_modified_time()
            except Exception as e:
                print(f"Error merging data: {e}")

    async def data_keys(self) -> list:
        """Return a list of keys in the data dictionary."""
        async with self._lock:
            try:
                return list(self._data.keys())
            except Exception as e:
                print(f"Error getting data keys: {e}")

    async def data_values(self) -> list:
        """Return a list of values in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    return [self.deserialize(self._mmapped_file[:], data_type) for data_type, _ in self._data.values()]
                return [v for _, v in self._data.values()]
            except Exception as e:
                print(f"Error getting data values: {e}")

    async def data_items(self) -> list:
        """Return a list of key-value pairs in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    return [(k, self.deserialize(self._mmapped_file[:], data_type)) for k, (data_type, _) in self._data.items()]
                return list(self._data.items())
            except Exception as e:
                print(f"Error getting data items: {e}")

    async def to_dict(self) -> dict:
        """Convert the MemorySlot instance to a dictionary."""
        async with self._lock:
            try:
                data = {}
                for k, (data_type, value) in self._data.items():
                    if isinstance(value, tuple):
                        if value[0] is not type(None):
                            data[k] = (value[0].__name__, value[1])
                    else:
                        data[k] = value
                return {
                    'memory_id': self._memory_id,
                    'name': self._name,
                    'operation_required': self._operation_required,
                    'data': data,
                    'metadata': self._metadata,
                    'created_at': self._created_at,
                    'modified_at': self._modified_at
                }
            except Exception as e:
                print(f"Error converting to dictionary: {e}")

    @staticmethod
    async def load_from_disk(data: dict) -> 'MemorySlot':
        """Initialize a MemorySlot instance from a dictionary."""
        try:
            dict_data = dict()
            slot_data = data.get('data', {})
            for k, v in slot_data.items():
                if isinstance(v, tuple):
                    _type = v[0]
                    dict_data[k] = (_type, v[1])
                else:
                    _type = type(v)
                    dict_data[k] = (_type, v)

            slot = MemorySlot(
                memory_id=data.get('memory_id', ''),
                name=data.get('name', ''),
                operation_required=data.get('operation_required', False),
                data=dict_data,
                file_path=data.get('file_path', None)
            )
            slot._metadata = data.get('metadata', {})
            slot._created_at = data.get('created_at', time.time())
            slot._modified_at = data.get('modified_at', slot._created_at)
            return slot
        except Exception as e:
            print(f"Error loading from dictionary: {e}")
