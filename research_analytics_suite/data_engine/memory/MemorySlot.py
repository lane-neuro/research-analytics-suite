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
import os
import pickle
import sys
import time
from mmap import mmap
from typing import Type

import aiosqlite
from research_analytics_suite.utils import CustomLogger, Config
from research_analytics_suite.operation_manager.operations.system.UpdateMonitor import UpdateMonitor


class MemorySlot:
    """
    A class to manage storage of data in an SQLite database and optionally using memory-mapped storage.

    Attributes:
        memory_id (str): A unique identifier for the memory slot.
        name (str): A name for the memory slot.
        data_type (type): The data type for the memory slot. Defaults to any.
        pointer (MemorySlot): A pointer to the next memory slot, if any.
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

    def __init__(self, memory_id: str, name: str, d_type: type, pointer: any, data: any, db_path: str,
                 file_path: str = None):
        """
        Initialize the MemorySlot instance.

        Args:
            memory_id (str): A unique identifier for the memory slot.
            name (str): A name for the memory slot.
            d_type (type): The data type for the memory slot.
            pointer (MemorySlot): A pointer to the next memory slot, if any.
            data (any): The data stored in the memory slot.
            db_path (str): The path to the SQLite database file.
            file_path (str): The file path for memory-mapped storage.
        """
        self._logger = CustomLogger()

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self._memory_id = memory_id
        self.name = name
        self.data_type = d_type
        self._pointer = pointer
        self._metadata = {}
        self._created_at = time.time()
        self._modified_at = None
        self._modified_at = self._created_at
        self._last_modified = None
        self._lock = asyncio.Lock()

        self.db_path = db_path
        self._file_path = file_path
        self._use_mmap = False
        self._mmapped_file = None
        self._file = None

        self._check_data_size(data)
        self._data = data
        self._update_operation = None

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
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_id ON variables (memory_id)"
            )
            await conn.commit()

            cursor = await conn.execute(
                "SELECT data FROM variables WHERE memory_id = ?",
                (self._memory_id,)
            )
            row = await cursor.fetchone()
            if not row and self.data:
                await self.set_data(self._data)

            # Create an update operation to update the data stored in the memory slot
            try:
                self._update_operation = await self._operation_control.operation_manager.create_operation(
                    operation_type=UpdateMonitor, name=f"slot_{self.memory_id}", action=self._update_data)
                self._update_operation.is_ready = True
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

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
    def data_type(self) -> type:
        """Gets the data type for the memory slot.

        Returns:
            Type: The data type for the memory slot.
        """
        return self._data_type

    @data_type.setter
    def data_type(self, value: type):
        """Sets the data type for the memory slot.

        Args:
            value (Type): The data type for the memory slot.
        """
        self._data_type = value

    @property
    def pointer(self) -> any:
        """Gets the pointer to the next memory slot.

        Returns:
            any: The pointer to the next memory slot.
        """
        return self._pointer

    @pointer.setter
    def pointer(self, value: any) -> None:
        """Sets the pointer to the next memory slot.

        Args:
            value (any): The pointer to the next memory slot.
        """
        if isinstance(value, MemorySlot):
            self._pointer = value
        else:
            self._pointer = None

    @property
    def data(self) -> any:
        """Gets the data stored in the memory slot.

        Returns:
            any: The data stored in the memory slot.
        """
        if self._pointer:
            return self._pointer.data
        return self._data

    @data.setter
    def data(self, value: any) -> None:
        """Sets the data stored in the memory slot."""
        self._data = value
        self._update_modified_time()

    async def set_data(self, value: any) -> None:
        """Stores the data within SQLite or memory-mapped file."""
        async with self._lock:
            self._check_data_size(value)
            if self._use_mmap:
                self._init_mmap(value)
            elif self._pointer is not None:
                self._pointer.data = value
            else:
                try:
                    async with aiosqlite.connect(self.db_path) as conn:
                        await conn.execute("INSERT OR REPLACE INTO variables (memory_id, name, data) VALUES (?, ?, ?)",
                            (self._memory_id, self.name, pickle.dumps(value))
                        )
                        await conn.commit()
                except Exception as e:
                    self._logger.error(Exception(f"[SQLite] Add variable error: {e}"), self.__class__.__name__)
                    return

            self.data = value

    async def _update_data(self) -> None:
        """Updates the data stored in the memory slot."""
        while not self._update_operation.is_running:
            await asyncio.sleep(.1)

        while self._update_operation.is_running:
            await asyncio.sleep(.01)
            if self._last_modified != self._modified_at:
                async with self._lock:
                    if self._use_mmap:
                        if self._mmapped_file:
                            self._mmapped_file.seek(0)
                            serialized_data = self._mmapped_file.read()
                            self._data = pickle.loads(serialized_data)
                            self._last_modified = self._modified_at
                    elif self._pointer:
                        self.data = self._pointer.data
                        self._last_modified = self._modified_at
                    else:
                        try:
                            await self.set_data(self._data)
                            self._last_modified = self._modified_at
                        except Exception as e:
                            self._logger.error(Exception(f"Failed to update data: {e}"), self.__class__.__name__)

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

    def export_as_csv(self):
        """
        Exports the data to a CSV file located
        """
        import csv

        if not self.data:
            self._logger.warning("No data to export.")
            return

        _config = Config()
        _path = os.path.join(_config.repr_path(_config.EXPORT_DIR), f"{self.name}-{self.memory_id}.csv")
        try:
            with open(_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                data = self.data

                if isinstance(data, list):
                    if data and isinstance(data[0], dict):
                        # List of dicts
                        fieldnames = set()
                        for entry in data:
                            fieldnames.update(entry.keys())
                        fieldnames = list(fieldnames)
                        dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        dict_writer.writeheader()
                        dict_writer.writerows(data)
                    elif data and isinstance(data[0], (list, tuple)):
                        # List of lists/tuples
                        writer.writerows(data)
                    else:
                        # List of simple values
                        for item in data:
                            writer.writerow([item])
                elif isinstance(data, dict):
                    _data = {}
                    for k, v in data.items():
                        if isinstance(v, (list, dict)):
                            _data[k] = ', '.join(map(str, v)) if isinstance(v, list) else str(v)
                        else:
                            _data[k] = v
                    writer.writerow(_data.keys())
                    writer.writerow(_data.values())
                else:
                    # Single value
                    writer.writerow([data])

            self._logger.info(f"Data exported to {_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to export data to CSV: {e}"), self.__class__.__name__)

    def _update_modified_time(self):
        """
        Updates the last modified timestamp.
        """
        self._modified_at = time.time()
        self._logger.debug(f"Memory slot modified at: {self._modified_at}")

    async def _delete_from_db(self) -> None:
        """Remove this slot's row from SQLite."""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute(
                    "DELETE FROM variables WHERE memory_id = ?",
                    (self._memory_id,)
                )
                await conn.commit()
            self._logger.debug(f"[SQLite] Deleted slot {self._memory_id}")
        except Exception as e:
            self._logger.error(Exception(f"[SQLite] Delete error: {e}"), self.__class__.__name__)

    def close(self):
        """
        Closes resources and removes this slot's data from SQLite.
        """
        # Best-effort stop of the update monitor
        try:
            if self._update_operation:
                self._update_operation.is_running = False
        except Exception:
            pass

        # Close mmap/file handles
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
