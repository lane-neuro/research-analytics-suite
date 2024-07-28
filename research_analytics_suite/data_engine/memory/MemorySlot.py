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
import aiosqlite
from research_analytics_suite.utils import CustomLogger


class MemorySlot:
    """
    A class to manage storage of data in an SQLite database and optionally using memory-mapped storage.

    Attributes:
        memory_id (str): A unique identifier for the memory slot.
        name (str): A name for the memory slot.
        data_type (type): The data type for the memory slot. Defaults to any.
        data (any): The data stored in the memory slot.
        metadata (dict): A dictionary to store additional metadata.
        created_at (float): The timestamp of when the memory slot was created.
        modified_at (float): The timestamp of when the memory slot was last modified.
        db_path (str): The path to the SQLite database file.
        _lock (asyncio.Lock): Lock to ensure thread-safe operations.
        _use_mmap (bool): Flag indicating whether to use memory-mapped storage.
        _file_path (str): The file path for memory-mapped storage.
        _mmapped_file (mmap): The memory-mapped file object.
        _file (file): The file object for memory-mapped storage.
    """
    DATA_SIZE_THRESHOLD = 2e6  # 2MB

    def __init__(self, memory_id: str, name: str, data: any, db_path: str, file_path: str = None):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            data (any): The data stored in the memory slot.
            db_path (str): The path to the SQLite database file.
            file_path (str): The file path for memory-mapped storage.
        """
        self._logger = CustomLogger()

        self._memory_id = memory_id
        self.name = name
        self._metadata = {}
        self._created_at = time.time()
        self._modified_at = self._created_at
        self._lock = asyncio.Lock()

        self.db_path = db_path
        self._file_path = file_path
        self._use_mmap = False
        self._mmapped_file = None
        self._file = None  # Ensure _file is always initialized

        self._check_data_size(data)
        self._initial_data = data

    async def setup(self) -> None:
        """
        Sets up the SQLite database and creates the variables table if it does not exist.
        If initial data is provided and the memory slot is not yet in the database, it sets the initial data.
        """
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS variables (
                    memory_id TEXT PRIMARY KEY,
                    name TEXT,
                    data BLOB
                )
            """)
            await conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_name ON variables (name)"
            )
            await conn.commit()

            cursor = await conn.execute(
                "SELECT data FROM variables WHERE memory_id = ?",
                (self._memory_id,)
            )
            row = await cursor.fetchone()
            if not row and self._initial_data is not None:
                await self.set_data(self._initial_data)

    @property
    def name(self) -> str:
        """Gets the name of the memory slot.

        Returns:
            str: The name of the memory slot.
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Sets the name of the memory slot.

        Args:
            value (str): The name of the memory slot.
        """
        self._name = value

    @property
    def memory_id(self) -> str:
        """Gets the unique identifier for the memory slot.

        Returns:
            str: The unique identifier for the memory slot.
        """
        return self._memory_id or ""

    @property
    def file_path(self) -> str:
        """Gets the file path for memory-mapped storage.

        Returns:
            str: The file path for memory-mapped storage.
        """
        return self._file_path or ""

    @property
    async def data(self) -> any:
        """Gets the data stored in the memory slot."""
        async with self._lock:
            if self._use_mmap:
                if self._mmapped_file:
                    self._mmapped_file.seek(0)
                    serialized_data = self._mmapped_file.read()
                    return pickle.loads(serialized_data)
            else:
                try:
                    async with aiosqlite.connect(self.db_path) as conn:
                        cursor = await conn.execute(
                            "SELECT data FROM variables WHERE memory_id = ?",
                            (self._memory_id,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            data = row[0]
                            return pickle.loads(data)
                        else:
                            return None
                except Exception as e:
                    self._logger.error(Exception(f"[SQLite] Get variable error: {e}"), self.__class__.__name__)

    async def set_data(self, value: any) -> None:
        """Stores the data within SQLite or memory-mapped file."""
        async with self._lock:
            self._check_data_size(value)
            if self._use_mmap:
                self._init_mmap(value)
            else:
                try:
                    async with aiosqlite.connect(self.db_path) as conn:
                        await conn.execute(
                            "INSERT OR REPLACE INTO variables (memory_id, name, data) VALUES (?, ?, ?)",
                            (self._memory_id, self._name, pickle.dumps(value))
                        )
                        await conn.commit()
                except Exception as e:
                    self._logger.error(Exception(f"[SQLite] Add variable error: {e}"), self.__class__.__name__)
            self._update_modified_time()

    def _check_data_size(self, _data) -> None:
        """
        Checks the size of the data and initializes memory-mapped storage if necessary.
        """
        data_size = sys.getsizeof(pickle.dumps(_data))
        if data_size > self.DATA_SIZE_THRESHOLD:
            if self._file_path:
                self._use_mmap = True
            else:
                self._file_path = f"{self._memory_id}.dat"

    def _init_mmap(self, value: any) -> None:
        """
        Initializes the memory-mapped file.
        """
        if not self._file_path:
            self._logger.error(Exception("File path must be provided for memory-mapped storage"),
                               self.__class__.__name__)
            return

        serialized_data = pickle.dumps(value)
        file_size = len(serialized_data)

        try:
            with open(self._file_path, 'wb') as f:
                f.truncate(file_size)  # Ensure the file is the right size
        except OSError as e:
            self._logger.error(Exception(f"Failed to initialize memory-mapped file: {e}"),
                               self.__class__.__name__)
            return

        self._file = open(self._file_path, 'r+b')
        self._mmapped_file = mmap(self._file.fileno(), file_size)

        self._dump_data_to_mmap(value)

    def _dump_data_to_mmap(self, value):
        """
        Dumps the data to the memory-mapped file.
        """
        self._mmapped_file.seek(0)
        serialized_data = pickle.dumps(value)
        self._mmapped_file.write(serialized_data)
        self._mmapped_file.flush()
        self._update_modified_time()
        self._logger.debug(f"Data dumped to memory-mapped file: {self._file_path}")

    def _update_modified_time(self):
        """
        Updates the last modified timestamp.
        """
        self._modified_at = time.time()
        self._logger.debug(f"Memory slot modified at: {self._modified_at}")

    def close(self):
        """
        Closes the memory-mapped file.
        """
        try:
            if self._mmapped_file:
                self._mmapped_file.close()
        except Exception as e:
            self._logger.warning(f"Failed to close memory-mapped file: {e}")

        try:
            if self._file:
                self._file.close()
        except Exception as e:
            self._logger.warning(f"Failed to close file: {e}")

    def __del__(self):
        self.close()
