import sys
import time
import asyncio
from mmap import mmap
from typing import Any, Type, Tuple, Dict

from research_analytics_suite.commands import command, register_commands

DATA_SIZE_THRESHOLD = 1024 * 1024  # 1 MB


@register_commands
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
        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        self._memory_id = memory_id
        self._name = name
        self._operation_required = operation_required
        self._data = data or {}
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
        return self._memory_id

    @memory_id.setter
    def memory_id(self, value: str):
        if not isinstance(value, str):
            self._logger.error(ValueError("memory_id must be a string"), self.__class__.__name__)
            return

        self._memory_id = value
        self.update_modified_time()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not isinstance(value, str):
            self._logger.error(ValueError("name must be a string"), self.__class__.__name__)
            return

        self._name = value
        self.update_modified_time()

    @property
    def operation_required(self) -> bool:
        return self._operation_required

    @operation_required.setter
    def operation_required(self, value: bool):
        if not isinstance(value, bool):
            self._logger.error(ValueError("operation_required must be a boolean"), self.__class__.__name__)
            return

        self._operation_required = value
        self.update_modified_time()

    @property
    def data(self) -> Dict[str, Tuple[Type, Any]]:
        return self._data

    @data.setter
    def data(self, value: Dict[str, Tuple[Type, Any]]):
        if value is None:
            self._data = {}

        elif not isinstance(value, dict):
            self._logger.error(ValueError("data must be a dictionary"), self.__class__.__name__)
            return

        for k, v in value.items() or {}:
            if not isinstance(k, str):
                self._logger.error(ValueError("All keys in data must be strings"), self.__class__.__name__)
                continue
            if not isinstance(v, tuple) or len(v) != 2:
                self._logger.error(ValueError("All values in data must be tuples of length 2"),
                                   self.__class__.__name__)
                continue

            t, v = v

            if not isinstance(v, t):
                self._logger.error(ValueError(f"Value for key '{k}' must be of type {t}"), self.__class__.__name__)
                continue

        self._data = value
        self.update_modified_time()

    @property
    def metadata(self) -> dict:
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict):
        if not isinstance(value, dict):
            self._logger.error(ValueError("metadata must be a dictionary"), self.__class__.__name__)
            return

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

    @command
    def check_data_size(self):
        try:
            data_size = sum(sys.getsizeof(value[1]) for value in self._data.values())
            self._file_size = data_size
            if data_size > DATA_SIZE_THRESHOLD:
                if self._file_path:
                    self._use_mmap = True
                    self._file_size = data_size
                    self.init_mmap()
                else:
                    self._logger.error(
                        Exception("File path must be provided for memory mapping when data size exceeds threshold."),
                        self.__class__.__name__)
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def init_mmap(self):
        """Initialize the memory-mapped file."""
        try:
            if not self._file_path:
                self._logger.error(ValueError("File path must be provided for memory-mapped storage"),
                                   self.__class__.__name__)
                return

            with open(self._file_path, 'wb') as f:
                f.write(b'\0' * self._file_size)

            self._file = open(self._file_path, 'r+b')
            self._mmapped_file = mmap(self._file.fileno(), self._file_size)

            self.dump_data_to_mmap()
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            if self._file:
                self._file.close()
            if self._mmapped_file:
                self._mmapped_file.close()

    def dump_data_to_mmap(self):
        try:
            self._mmapped_file[:] = b'\0' * self._file_size

            offset = 0
            for key, (data_type, value) in self._data.items():
                serialized_value = self.serialize(value)
                size = len(serialized_value)
                self._mmapped_file[offset:offset + size] = serialized_value
                offset += size
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def serialize(self, value):
        """Serialize a value for storage in mmap."""
        try:
            if isinstance(value, str):
                return value.encode('utf-8')
            elif isinstance(value, (int, float)):
                return str(value).encode('utf-8')
            elif isinstance(value, bytes):
                return value
            else:
                raise TypeError(f"Unsupported data type: {type(value).__name__}")
        except Exception as e:
            self._logger.error(Exception(f"Serialization error for value '{value}': {e}", self.__class__.__name__))
            return b''

    def deserialize(self, value, data_type):
        """Deserialize a value from mmap."""
        try:
            return data_type(value.decode('utf-8'))
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            return None

    def close_mmap(self):
        """Close the memory-mapped file."""
        try:
            if self._mmapped_file:
                self._mmapped_file.close()
                self._file.close()
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)

    def update_modified_time(self):
        """Update the last modified timestamp."""
        self._modified_at = time.time()

    @command
    def validate_data(self) -> bool:
        """Validate the data dictionary."""
        _valid = True
        if self._data is None:
            self._data = {}
        else:
            for k, (t, v) in self._data.items():
                if not isinstance(k, str):
                    self._logger.error(ValueError("All keys in data must be strings"), self.__class__.__name__)
                    _valid = False
                    break
                if not isinstance(v, t):
                    self._logger.error(ValueError(f"Value for key '{k}' must be of type {t}"), self.__class__.__name__)
                    _valid = False
                    break

        return _valid

    @command
    async def get_data_by_key(self, key: str) -> Any:
        """Retrieve the value associated with a specific key."""
        async with self._lock:
            try:
                if self._use_mmap:
                    offset = self.calculate_offset(key)
                    size = len(self.serialize(self._data[key][1]))
                    return self.deserialize(self._mmapped_file[offset:offset + size], self._data[key][0])
                return self._data.get(key, (None, None))[1]
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)
                return None

    @command
    async def get_data_type_by_key(self, key: str) -> type:
        """Retrieve the data type associated with a specific key."""
        async with self._lock:
            return self._data.get(key, (None, None))[0]

    @command
    async def set_data_by_key(self, key: str, value: Any, data_type: Type):
        """Set the value for a specific key."""
        if not isinstance(key, str):
            self._logger.error(TypeError(f"Key {key} must be a string"), self.__class__.__name__)
        if not isinstance(value, data_type):
            self._logger.error(TypeError(f"Value {value} must be of type {data_type}"), self.__class__.__name__)

        async with self._lock:
            self._data[key] = (data_type, value)
            self.check_data_size()  # Check data size and potentially initialize memory mapping
            self.update_modified_time()
            if self._use_mmap:
                self.dump_data_to_mmap()

    @command
    async def remove_data_by_key(self, key: str):
        """Remove the key-value pair associated with a specific key."""
        async with self._lock:
            try:
                if key in self._data:
                    if self._use_mmap:
                        offset = self.calculate_offset(key)
                        size = len(self.serialize(self._data[key][1]))
                        self._mmapped_file[offset:offset + size] = b'\0' * size
                    del self._data[key]
                    self.update_modified_time()
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def clear_data(self):
        """Clear all data in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    self._mmapped_file[:] = b'\0' * self._file_size
                self._data.clear()
                self.update_modified_time()
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def has_key(self, key: str) -> bool:
        """Check if a specific key exists in the data dictionary."""
        async with self._lock:
            return key in self._data

    def calculate_offset(self, key: str) -> int:
        """Calculate the offset for a key in the mmap file."""
        _offset = 0
        for k in self._data.keys():
            if k == key:
                break
            try:
                _data_type, _value = self._data[k]
                if self._use_mmap:
                    _offset += len(self.serialize(_value))
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)
                _offset = 0
                break

        return _offset

    @command
    async def update_data(self, data: Dict[str, Tuple[Type, Any]]):
        """Update multiple key-value pairs in the data dictionary."""
        if not isinstance(data, dict):
            self._logger.error(ValueError("data must be a dictionary"), self.__class__.__name__)
            return

        for k, (t, v) in data.items():
            if not isinstance(k, str):
                self._logger.error(ValueError("All keys in data must be strings"), self.__class__.__name__)
                return
            if not isinstance(v, t):
                self._logger.error(ValueError(f"Value for key '{k}' must be of type {t}"), self.__class__.__name__)
                return

        async with self._lock:
            try:
                if self._use_mmap:
                    for key, (data_type, value) in data.items():
                        await self.set_data_by_key(key, value, data_type)
                else:
                    self._data.update(data)
                self.update_modified_time()
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def merge_data(self, data: Dict[str, Tuple[Type, Any]]):
        """Merge another dictionary into the data dictionary."""
        if not isinstance(data, dict):
            self._logger.error(ValueError("data must be a dictionary"), self.__class__.__name__)
            return

        for k, (t, v) in data.items():
            if not isinstance(k, str):
                self._logger.error(ValueError("All keys in data must be strings"), self.__class__.__name__)
                return
            if not isinstance(v, t):
                self._logger.error(ValueError(f"Value for key '{k}' must be of type {t}"), self.__class__.__name__)
                return

        async with self._lock:
            try:
                if self._use_mmap:
                    for key, (data_type, value) in data.items():
                        await self.set_data_by_key(key, value, data_type)
                else:
                    self._data = {**self._data, **data}
                self.update_modified_time()
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def data_keys(self) -> list:
        """Return a list of keys in the data dictionary."""
        async with self._lock:
            try:
                return list(self._data.keys())
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def data_values(self) -> list:
        """Return a list of values in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    return [self.deserialize(self._mmapped_file[self.calculate_offset(key):], data_type) for
                            key, (data_type, _) in self._data.items()]
                return [v for _, v in self._data.values()]
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
    async def data_items(self) -> list:
        """Return a list of key-value pairs in the data dictionary."""
        async with self._lock:
            try:
                if self._use_mmap:
                    return [(k, self.deserialize(self._mmapped_file[self.calculate_offset(k):], data_type)) for
                            k, (data_type, _) in self._data.items()]
                return list(self._data.items())
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    @command
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
                self._logger.error(e, self.__class__.__name__)

    @staticmethod
    @command
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
            raise ValueError(f"Error loading MemorySlot from disk: {e}")
