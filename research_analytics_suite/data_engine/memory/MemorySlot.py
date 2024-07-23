"""
MemorySlot Module

This module defines the MemorySlot class, which represents a memory slot for storing data.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import asyncio
import pickle
import sys
import time
from mmap import mmap


class MemorySlot:
    """
    A class representing a memory slot for storing data.

    Attributes:
        memory_id (str): A unique identifier for the memory slot.
        name (str): A name for the memory slot.
        data_type (type): The data type for the memory slot. Defaults to any.
        data (any): The data stored in the memory slot.
        metadata (dict): A dictionary to store additional metadata.
        created_at (float): The timestamp of when the memory slot was created.
        modified_at (float): The timestamp of when the memory slot was last modified.
        _lock (asyncio.Lock): Lock to ensure thread-safe operations.
        _use_mmap (bool): Flag indicating whether to use memory-mapped storage.
        _file_path (str): The file path for memory-mapped storage.
        _mmapped_file (mmap): The memory-mapped file object.
        _file (file): The file object for memory-mapped storage.
    """
    DATA_SIZE_THRESHOLD = 2e6  # 2MB

    def __init__(self, memory_id: str, name: str, data: any, file_path: str = None):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            data (any): The data stored in the memory slot.
            file_path (str): The file path for memory-mapped storage.
        """
        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        self._memory_id = memory_id
        self._name = name
        self._data = data
        self._metadata = {}
        self._created_at = time.time()
        self._modified_at = self._created_at
        self._lock = asyncio.Lock()

        self._file_path = file_path
        self._use_mmap = False
        self._mmapped_file = None
        self._file = None  # Ensure _file is always initialized

        self.check_data_size()

    def check_data_size(self) -> None:
        """
        Checks the size of the data and initializes memory-mapped storage if necessary.
        """
        data_size = sys.getsizeof(self._data)
        if data_size > self.DATA_SIZE_THRESHOLD:
            if self._file_path:
                self._use_mmap = True
                self._init_mmap()
            else:
                self._logger.error(
                    Exception("File path must be provided for memory mapping when data size exceeds threshold."),
                    self.__class__.__name__)

    def _init_mmap(self):
        """
        Initializes the memory-mapped file.
        """
        if not self._file_path:
            self._logger.error(ValueError("File path must be provided for memory-mapped storage"),
                               self.__class__.__name__)
            return

        with open(self._file_path, 'wb') as f:
            f.write(b'\0' * sys.getsizeof(self._data))

        self._file = open(self._file_path, 'r+b')
        self._mmapped_file = mmap(self._file.fileno(), 0)

        self._dump_data_to_mmap()

    def _dump_data_to_mmap(self):
        """
        Dumps the data to the memory-mapped file.
        """
        serialized_data = pickle.dumps(self._data)
        self._mmapped_file.write(serialized_data)

    def get_data(self):
        """
        Retrieves the data stored in the memory slot.

        Returns:
            any: The data stored in the memory slot.
        """
        if self._mmapped_file:
            self._mmapped_file.seek(0)
            serialized_data = self._mmapped_file.read()
            return pickle.loads(serialized_data)
        return self._data

    def set_data(self, value: any):
        """
        Sets the data stored in the memory slot.

        Args:
            value (any): The data to store in the memory slot.
        """
        self._data = value
        self._update_modified_time()
        if self._use_mmap:
            self._dump_data_to_mmap()

    def _update_modified_time(self):
        """
        Updates the last modified timestamp.
        """
        self._modified_at = time.time()

    @property
    def memory_id(self):
        return self._memory_id

    @property
    def name(self):
        return self._name

    @property
    def data(self):
        return self.get_data()

    def close(self):
        """
        Closes the memory-mapped file.
        """
        if self._mmapped_file:
            self._mmapped_file.close()
        if self._file:
            self._file.close()

    def __del__(self):
        self.close()
