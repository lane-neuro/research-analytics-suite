"""
StorageBackend Module

Universal storage abstraction layer that provides unified access to any storage system.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Development
"""
from __future__ import annotations

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import shutil

from research_analytics_suite.utils.CustomLogger import CustomLogger


class StorageBackend(ABC):
    """
    Abstract base class for all storage backends.

    Provides a unified interface for accessing any storage system,
    from local filesystems to cloud storage and databases.
    """

    def __init__(self, name: str, scheme: str):
        """
        Initialize the storage backend.

        Args:
            name: Human-readable name of the backend
            scheme: URL scheme this backend handles (e.g., 's3', 'file', 'hdfs')
        """
        self.name = name
        self.scheme = scheme
        self._logger = CustomLogger()

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """
        Check if a path exists.

        Args:
            path: Path to check

        Returns:
            True if path exists
        """
        pass

    @abstractmethod
    async def is_file(self, path: str) -> bool:
        """
        Check if a path is a file.

        Args:
            path: Path to check

        Returns:
            True if path is a file
        """
        pass

    @abstractmethod
    async def is_directory(self, path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check

        Returns:
            True if path is a directory
        """
        pass

    @abstractmethod
    async def get_size(self, path: str) -> int:
        """
        Get the size of a file.

        Args:
            path: Path to file

        Returns:
            Size in bytes
        """
        pass

    @abstractmethod
    async def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory.

        Args:
            path: Directory path
            pattern: File pattern to match

        Returns:
            List of file paths
        """
        pass

    @abstractmethod
    async def read_bytes(self, path: str, start: int = 0,
                        length: Optional[int] = None) -> bytes:
        """
        Read bytes from a file.

        Args:
            path: File path
            start: Starting byte position
            length: Number of bytes to read (None for all)

        Returns:
            File content as bytes
        """
        pass

    @abstractmethod
    async def write_bytes(self, path: str, data: bytes,
                         append: bool = False) -> bool:
        """
        Write bytes to a file.

        Args:
            path: File path
            data: Data to write
            append: Whether to append to existing file

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """
        Delete a file or directory.

        Args:
            path: Path to delete

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def move(self, source: str, destination: str) -> bool:
        """
        Move a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def create_directory(self, path: str) -> bool:
        """
        Create a directory.

        Args:
            path: Directory path to create

        Returns:
            True if successful
        """
        pass

    async def read_text(self, path: str, encoding: str = 'utf-8') -> str:
        """
        Read text from a file.

        Args:
            path: File path
            encoding: Text encoding

        Returns:
            File content as string
        """
        data = await self.read_bytes(path)
        return data.decode(encoding)

    async def write_text(self, path: str, content: str,
                        encoding: str = 'utf-8', append: bool = False) -> bool:
        """
        Write text to a file.

        Args:
            path: File path
            content: Text content to write
            encoding: Text encoding
            append: Whether to append to existing file

        Returns:
            True if successful
        """
        data = content.encode(encoding)
        return await self.write_bytes(path, data, append)

    async def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a path.

        Args:
            path: Path to analyze

        Returns:
            Metadata dictionary
        """
        metadata = {
            'path': path,
            'exists': await self.exists(path),
            'is_file': False,
            'is_directory': False,
            'size': 0
        }

        if metadata['exists']:
            metadata['is_file'] = await self.is_file(path)
            metadata['is_directory'] = await self.is_directory(path)
            if metadata['is_file']:
                metadata['size'] = await self.get_size(path)

        return metadata

    async def stream_read(self, path: str, chunk_size: int = 1024*1024) -> AsyncIterator[bytes]:
        """
        Stream read a file in chunks.

        Args:
            path: File path
            chunk_size: Size of each chunk

        Yields:
            Data chunks
        """
        total_size = await self.get_size(path)
        start = 0

        while start < total_size:
            end = min(start + chunk_size, total_size)
            chunk = await self.read_bytes(path, start, end - start)
            yield chunk
            start = end

    def can_handle(self, path: str) -> bool:
        """
        Check if this backend can handle the given path.

        Args:
            path: Path to check

        Returns:
            True if this backend can handle the path
        """
        parsed = urlparse(path)
        return parsed.scheme == self.scheme or (not parsed.scheme and self.scheme == 'file')

    def normalize_path(self, path: str) -> str:
        """
        Normalize a path for this backend.

        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        return path

    async def sync_from(self, source_backend: 'StorageBackend',
                       source_path: str, dest_path: str) -> bool:
        """
        Sync data from another storage backend.

        Args:
            source_backend: Source storage backend
            source_path: Source path
            dest_path: Destination path

        Returns:
            True if successful
        """
        try:
            # Stream data between backends
            async for chunk in source_backend.stream_read(source_path):
                await self.write_bytes(dest_path, chunk, append=True)
            return True
        except Exception as e:
            self._logger.error(f"Sync failed from {source_path} to {dest_path}: {e}")
            return False


class LocalFileSystem(StorageBackend):
    """Local filesystem storage backend."""

    def __init__(self):
        """Initialize local filesystem backend."""
        super().__init__("Local FileSystem", "file")

    async def exists(self, path: str) -> bool:
        """Check if a path exists."""
        return os.path.exists(path)

    async def is_file(self, path: str) -> bool:
        """Check if a path is a file."""
        return os.path.isfile(path)

    async def is_directory(self, path: str) -> bool:
        """Check if a path is a directory."""
        return os.path.isdir(path)

    async def get_size(self, path: str) -> int:
        """Get the size of a file."""
        return os.path.getsize(path)

    async def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """List files in a directory."""
        from glob import glob
        search_pattern = os.path.join(path, pattern)
        return glob(search_pattern)

    async def read_bytes(self, path: str, start: int = 0,
                        length: Optional[int] = None) -> bytes:
        """Read bytes from a file."""
        with open(path, 'rb') as f:
            f.seek(start)
            if length is None:
                return f.read()
            else:
                return f.read(length)

    async def write_bytes(self, path: str, data: bytes,
                         append: bool = False) -> bool:
        """Write bytes to a file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)

            mode = 'ab' if append else 'wb'
            with open(path, mode) as f:
                f.write(data)
            return True
        except Exception as e:
            self._logger.error(f"Failed to write to {path}: {e}")
            return False

    async def delete(self, path: str) -> bool:
        """Delete a file or directory."""
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except Exception as e:
            self._logger.error(f"Failed to delete {path}: {e}")
            return False

    async def copy(self, source: str, destination: str) -> bool:
        """Copy a file or directory."""
        try:
            if os.path.isfile(source):
                shutil.copy2(source, destination)
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
            return True
        except Exception as e:
            self._logger.error(f"Failed to copy {source} to {destination}: {e}")
            return False

    async def move(self, source: str, destination: str) -> bool:
        """Move a file or directory."""
        try:
            shutil.move(source, destination)
            return True
        except Exception as e:
            self._logger.error(f"Failed to move {source} to {destination}: {e}")
            return False

    async def create_directory(self, path: str) -> bool:
        """Create a directory."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            self._logger.error(f"Failed to create directory {path}: {e}")
            return False


class InMemoryStorage(StorageBackend):
    """In-memory storage backend for temporary data."""

    def __init__(self):
        """Initialize in-memory storage backend."""
        super().__init__("In-Memory Storage", "memory")
        self._files: Dict[str, bytes] = {}
        self._directories: set = set()

    async def exists(self, path: str) -> bool:
        """Check if a path exists."""
        return path in self._files or path in self._directories

    async def is_file(self, path: str) -> bool:
        """Check if a path is a file."""
        return path in self._files

    async def is_directory(self, path: str) -> bool:
        """Check if a path is a directory."""
        return path in self._directories

    async def get_size(self, path: str) -> int:
        """Get the size of a file."""
        if path in self._files:
            return len(self._files[path])
        return 0

    async def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """List files in a directory."""
        import fnmatch
        files = []
        for file_path in self._files.keys():
            if file_path.startswith(path):
                relative = file_path[len(path):].lstrip('/')
                if '/' not in relative and fnmatch.fnmatch(relative, pattern):
                    files.append(file_path)
        return files

    async def read_bytes(self, path: str, start: int = 0,
                        length: Optional[int] = None) -> bytes:
        """Read bytes from a file."""
        if path not in self._files:
            raise FileNotFoundError(f"File not found: {path}")

        data = self._files[path]
        if length is None:
            return data[start:]
        else:
            return data[start:start + length]

    async def write_bytes(self, path: str, data: bytes,
                         append: bool = False) -> bool:
        """Write bytes to a file."""
        try:
            if append and path in self._files:
                self._files[path] += data
            else:
                self._files[path] = data

            # Create parent directories
            parent = os.path.dirname(path)
            if parent:
                self._directories.add(parent)

            return True
        except Exception as e:
            self._logger.error(f"Failed to write to {path}: {e}")
            return False

    async def delete(self, path: str) -> bool:
        """Delete a file or directory."""
        try:
            if path in self._files:
                del self._files[path]
            elif path in self._directories:
                self._directories.remove(path)
                # Remove files in directory
                to_remove = [f for f in self._files.keys() if f.startswith(path + '/')]
                for f in to_remove:
                    del self._files[f]
            return True
        except Exception as e:
            self._logger.error(f"Failed to delete {path}: {e}")
            return False

    async def copy(self, source: str, destination: str) -> bool:
        """Copy a file or directory."""
        try:
            if source in self._files:
                self._files[destination] = self._files[source]
            return True
        except Exception as e:
            self._logger.error(f"Failed to copy {source} to {destination}: {e}")
            return False

    async def move(self, source: str, destination: str) -> bool:
        """Move a file or directory."""
        try:
            if source in self._files:
                self._files[destination] = self._files.pop(source)
            return True
        except Exception as e:
            self._logger.error(f"Failed to move {source} to {destination}: {e}")
            return False

    async def create_directory(self, path: str) -> bool:
        """Create a directory."""
        self._directories.add(path)
        return True


class TemporaryStorage(StorageBackend):
    """Temporary storage backend using system temp directory."""

    def __init__(self):
        """Initialize temporary storage backend."""
        super().__init__("Temporary Storage", "temp")
        self._temp_dir = tempfile.mkdtemp(prefix="ras_temp_")
        self._local_fs = LocalFileSystem()

    def _get_temp_path(self, path: str) -> str:
        """Convert path to temporary directory path."""
        # Remove any leading scheme
        if path.startswith('temp://'):
            path = path[7:]
        return os.path.join(self._temp_dir, path.lstrip('/'))

    async def exists(self, path: str) -> bool:
        """Check if a path exists."""
        return await self._local_fs.exists(self._get_temp_path(path))

    async def is_file(self, path: str) -> bool:
        """Check if a path is a file."""
        return await self._local_fs.is_file(self._get_temp_path(path))

    async def is_directory(self, path: str) -> bool:
        """Check if a path is a directory."""
        return await self._local_fs.is_directory(self._get_temp_path(path))

    async def get_size(self, path: str) -> int:
        """Get the size of a file."""
        return await self._local_fs.get_size(self._get_temp_path(path))

    async def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """List files in a directory."""
        temp_files = await self._local_fs.list_files(self._get_temp_path(path), pattern)
        # Convert back to temp:// scheme
        return [f"temp://{os.path.relpath(f, self._temp_dir)}" for f in temp_files]

    async def read_bytes(self, path: str, start: int = 0,
                        length: Optional[int] = None) -> bytes:
        """Read bytes from a file."""
        return await self._local_fs.read_bytes(self._get_temp_path(path), start, length)

    async def write_bytes(self, path: str, data: bytes,
                         append: bool = False) -> bool:
        """Write bytes to a file."""
        return await self._local_fs.write_bytes(self._get_temp_path(path), data, append)

    async def delete(self, path: str) -> bool:
        """Delete a file or directory."""
        return await self._local_fs.delete(self._get_temp_path(path))

    async def copy(self, source: str, destination: str) -> bool:
        """Copy a file or directory."""
        return await self._local_fs.copy(
            self._get_temp_path(source),
            self._get_temp_path(destination)
        )

    async def move(self, source: str, destination: str) -> bool:
        """Move a file or directory."""
        return await self._local_fs.move(
            self._get_temp_path(source),
            self._get_temp_path(destination)
        )

    async def create_directory(self, path: str) -> bool:
        """Create a directory."""
        return await self._local_fs.create_directory(self._get_temp_path(path))

    def cleanup(self) -> None:
        """Clean up temporary directory."""
        try:
            shutil.rmtree(self._temp_dir)
        except Exception as e:
            pass

    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()


class CloudStorageBase(StorageBackend):
    """Base class for cloud storage backends."""

    def __init__(self, name: str, scheme: str):
        """Initialize cloud storage backend."""
        super().__init__(name, scheme)
        self._client = None

    @abstractmethod
    async def authenticate(self, **credentials) -> bool:
        """
        Authenticate with the cloud service.

        Args:
            **credentials: Authentication credentials

        Returns:
            True if authentication successful
        """
        pass

    @abstractmethod
    async def list_buckets(self) -> List[str]:
        """
        List available buckets/containers.

        Returns:
            List of bucket names
        """
        pass

    async def get_presigned_url(self, path: str, expiration: int = 3600) -> str:
        """
        Get a presigned URL for temporary access.

        Args:
            path: Object path
            expiration: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        raise NotImplementedError("Presigned URLs not supported by this backend")

    def parse_cloud_path(self, path: str) -> tuple[str, str]:
        """
        Parse cloud path into bucket and key.

        Args:
            path: Cloud path (e.g., s3://bucket/key)

        Returns:
            Tuple of (bucket, key)
        """
        parsed = urlparse(path)
        bucket = parsed.netloc
        key = parsed.path.lstrip('/')
        return bucket, key
