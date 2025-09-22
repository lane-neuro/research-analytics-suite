"""
StorageLayer Module

Universal storage layer that provides unified access to any storage system.
Automatically routes operations to the appropriate storage backend.

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

import asyncio
from typing import Dict, List, Optional, Any, AsyncIterator
from urllib.parse import urlparse
import os

from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.data_engine.storage.StorageBackend import (
    StorageBackend, LocalFileSystem, InMemoryStorage, TemporaryStorage
)


class StorageLayer:
    """
    Universal storage layer that manages multiple storage backends.

    Provides a unified interface for accessing any storage system by
    automatically routing operations to the appropriate backend.
    """

    def __init__(self):
        """Initialize the storage layer."""
        self._logger = CustomLogger()
        self._backends: Dict[str, StorageBackend] = {}
        self._default_backend = None

        # Register built-in backends
        self._register_builtin_backends()

    def _register_builtin_backends(self) -> None:
        """Register built-in storage backends."""
        self.register_backend(LocalFileSystem())
        self.register_backend(InMemoryStorage())
        self.register_backend(TemporaryStorage())

        # Set local filesystem as default
        self._default_backend = self._backends['file']

    def register_backend(self, backend: StorageBackend) -> None:
        """
        Register a storage backend.

        Args:
            backend: Storage backend to register
        """
        self._backends[backend.scheme] = backend
        self._logger.debug(f"Registered storage backend: {backend.name} ({backend.scheme})")

    def unregister_backend(self, scheme: str) -> bool:
        """
        Unregister a storage backend.

        Args:
            scheme: URL scheme of backend to remove

        Returns:
            True if backend was found and removed
        """
        if scheme in self._backends:
            backend = self._backends.pop(scheme)
            self._logger.debug(f"Unregistered storage backend: {backend.name}")
            return True
        return False

    def get_backend(self, path: str) -> StorageBackend:
        """
        Get the appropriate backend for a path.

        Args:
            path: File/directory path

        Returns:
            Storage backend that can handle the path

        Raises:
            ValueError: If no suitable backend found
        """
        parsed = urlparse(path)
        scheme = parsed.scheme if parsed.scheme else 'file'

        if scheme in self._backends:
            return self._backends[scheme]
        elif self._default_backend:
            return self._default_backend
        else:
            raise ValueError(f"No storage backend found for scheme: {scheme}")

    def list_backends(self) -> Dict[str, str]:
        """
        List all registered backends.

        Returns:
            Dictionary mapping schemes to backend names
        """
        return {scheme: backend.name for scheme, backend in self._backends.items()}

    async def exists(self, path: str) -> bool:
        """
        Check if a path exists.

        Args:
            path: Path to check

        Returns:
            True if path exists
        """
        backend = self.get_backend(path)
        return await backend.exists(path)

    async def is_file(self, path: str) -> bool:
        """
        Check if a path is a file.

        Args:
            path: Path to check

        Returns:
            True if path is a file
        """
        backend = self.get_backend(path)
        return await backend.is_file(path)

    async def is_directory(self, path: str) -> bool:
        """
        Check if a path is a directory.

        Args:
            path: Path to check

        Returns:
            True if path is a directory
        """
        backend = self.get_backend(path)
        return await backend.is_directory(path)

    async def get_size(self, path: str) -> int:
        """
        Get the size of a file.

        Args:
            path: Path to file

        Returns:
            Size in bytes
        """
        backend = self.get_backend(path)
        return await backend.get_size(path)

    async def list_files(self, path: str, pattern: str = "*") -> List[str]:
        """
        List files in a directory.

        Args:
            path: Directory path
            pattern: File pattern to match

        Returns:
            List of file paths
        """
        backend = self.get_backend(path)
        return await backend.list_files(path, pattern)

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
        backend = self.get_backend(path)
        return await backend.read_bytes(path, start, length)

    async def read_text(self, path: str, encoding: str = 'utf-8') -> str:
        """
        Read text from a file.

        Args:
            path: File path
            encoding: Text encoding

        Returns:
            File content as string
        """
        backend = self.get_backend(path)
        return await backend.read_text(path, encoding)

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
        backend = self.get_backend(path)
        return await backend.write_bytes(path, data, append)

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
        backend = self.get_backend(path)
        return await backend.write_text(path, content, encoding, append)

    async def delete(self, path: str) -> bool:
        """
        Delete a file or directory.

        Args:
            path: Path to delete

        Returns:
            True if successful
        """
        backend = self.get_backend(path)
        return await backend.delete(path)

    async def copy(self, source: str, destination: str) -> bool:
        """
        Copy a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            True if successful
        """
        source_backend = self.get_backend(source)
        dest_backend = self.get_backend(destination)

        if source_backend == dest_backend:
            # Same backend - use native copy
            return await source_backend.copy(source, destination)
        else:
            # Cross-backend copy - stream data
            return await dest_backend.sync_from(source_backend, source, destination)

    async def move(self, source: str, destination: str) -> bool:
        """
        Move a file or directory.

        Args:
            source: Source path
            destination: Destination path

        Returns:
            True if successful
        """
        # Try copy then delete for cross-backend moves
        if await self.copy(source, destination):
            return await self.delete(source)
        return False

    async def create_directory(self, path: str) -> bool:
        """
        Create a directory.

        Args:
            path: Directory path to create

        Returns:
            True if successful
        """
        backend = self.get_backend(path)
        return await backend.create_directory(path)

    async def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a path.

        Args:
            path: Path to analyze

        Returns:
            Metadata dictionary
        """
        backend = self.get_backend(path)
        metadata = await backend.get_metadata(path)
        metadata['backend'] = backend.name
        metadata['scheme'] = backend.scheme
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
        backend = self.get_backend(path)
        async for chunk in backend.stream_read(path, chunk_size):
            yield chunk

    async def sync_directories(self, source_dir: str, dest_dir: str,
                              delete_extra: bool = False) -> Dict[str, Any]:
        """
        Synchronize two directories.

        Args:
            source_dir: Source directory path
            dest_dir: Destination directory path
            delete_extra: Whether to delete files in dest not in source

        Returns:
            Sync results
        """
        results = {
            'copied': [],
            'updated': [],
            'deleted': [],
            'errors': []
        }

        try:
            # Ensure destination directory exists
            await self.create_directory(dest_dir)

            # Get list of files in source
            source_files = await self.list_files(source_dir, "**/*")
            dest_files = set(await self.list_files(dest_dir, "**/*"))

            for source_file in source_files:
                try:
                    # Calculate relative path
                    rel_path = os.path.relpath(source_file, source_dir)
                    dest_file = os.path.join(dest_dir, rel_path)

                    # Check if file needs to be copied/updated
                    if not await self.exists(dest_file):
                        await self.copy(source_file, dest_file)
                        results['copied'].append(rel_path)
                    else:
                        # Compare sizes/timestamps if possible
                        source_size = await self.get_size(source_file)
                        dest_size = await self.get_size(dest_file)
                        if source_size != dest_size:
                            await self.copy(source_file, dest_file)
                            results['updated'].append(rel_path)

                    dest_files.discard(dest_file)

                except Exception as e:
                    results['errors'].append(f"Error syncing {source_file}: {e}")

            # Delete extra files if requested
            if delete_extra:
                for extra_file in dest_files:
                    try:
                        await self.delete(extra_file)
                        rel_path = os.path.relpath(extra_file, dest_dir)
                        results['deleted'].append(rel_path)
                    except Exception as e:
                        results['errors'].append(f"Error deleting {extra_file}: {e}")

        except Exception as e:
            results['errors'].append(f"Sync failed: {e}")

        return results

    async def find_files(self, base_path: str, pattern: str = "*",
                        recursive: bool = True) -> List[str]:
        """
        Find files matching a pattern.

        Args:
            base_path: Base directory to search
            pattern: File pattern to match
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        files = []

        if recursive:
            # Recursive search
            pattern = f"**/{pattern}"

        try:
            files = await self.list_files(base_path, pattern)
        except Exception as e:
            self._logger.error(f"Error finding files in {base_path}: {e}")

        return files

    async def get_storage_stats(self, path: str) -> Dict[str, Any]:
        """
        Get storage statistics for a path.

        Args:
            path: Path to analyze

        Returns:
            Storage statistics
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'largest_files': []
        }

        try:
            if await self.is_file(path):
                size = await self.get_size(path)
                stats['total_files'] = 1
                stats['total_size'] = size
                ext = os.path.splitext(path)[1].lower()
                stats['file_types'][ext] = 1
                stats['largest_files'] = [(path, size)]
            elif await self.is_directory(path):
                files = await self.find_files(path, "*", recursive=True)
                file_sizes = []

                for file_path in files:
                    try:
                        size = await self.get_size(file_path)
                        stats['total_size'] += size
                        file_sizes.append((file_path, size))

                        ext = os.path.splitext(file_path)[1].lower()
                        stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                    except Exception as e:
                        self._logger.warning(f"Error getting size for {file_path}: {e}")

                stats['total_files'] = len(files)
                # Sort by size and get top 10 largest files
                file_sizes.sort(key=lambda x: x[1], reverse=True)
                stats['largest_files'] = file_sizes[:10]

        except Exception as e:
            self._logger.error(f"Error getting storage stats for {path}: {e}")

        return stats

    def get_temp_path(self, filename: str = "") -> str:
        """
        Get a temporary file path.

        Args:
            filename: Optional filename

        Returns:
            Temporary file path
        """
        if 'temp' in self._backends:
            base_path = "temp://data"
            if filename:
                return f"{base_path}/{filename}"
            else:
                import uuid
                return f"{base_path}/{uuid.uuid4().hex}"
        else:
            import tempfile
            return tempfile.mktemp(suffix=filename)

    async def create_temp_file(self, content: bytes = b"",
                             filename: str = "") -> str:
        """
        Create a temporary file with content.

        Args:
            content: File content
            filename: Optional filename

        Returns:
            Path to temporary file
        """
        temp_path = self.get_temp_path(filename)
        await self.write_bytes(temp_path, content)
        return temp_path

    async def cleanup_temp_storage(self) -> None:
        """Clean up temporary storage."""
        if 'temp' in self._backends:
            temp_backend = self._backends['temp']
            if hasattr(temp_backend, 'cleanup'):
                temp_backend.cleanup()

    def get_backend_stats(self) -> Dict[str, Any]:
        """
        Get statistics about registered backends.

        Returns:
            Backend statistics
        """
        return {
            'total_backends': len(self._backends),
            'backends': self.list_backends(),
            'default_backend': self._default_backend.name if self._default_backend else None
        }

    async def test_backend(self, scheme: str) -> Dict[str, Any]:
        """
        Test a storage backend with basic operations.

        Args:
            scheme: Backend scheme to test

        Returns:
            Test results
        """
        if scheme not in self._backends:
            return {'error': f'Backend {scheme} not found'}

        backend = self._backends[scheme]
        test_results = {
            'backend': backend.name,
            'scheme': scheme,
            'tests': {}
        }

        # Test basic operations
        test_path = f"{scheme}://test_file.txt" if scheme != 'file' else "/tmp/test_file.txt"
        test_content = b"Hello, World!"

        try:
            # Test write
            success = await backend.write_bytes(test_path, test_content)
            test_results['tests']['write'] = success

            # Test read
            if success:
                data = await backend.read_bytes(test_path)
                test_results['tests']['read'] = data == test_content

            # Test exists
            test_results['tests']['exists'] = await backend.exists(test_path)

            # Test delete
            test_results['tests']['delete'] = await backend.delete(test_path)

        except Exception as e:
            test_results['tests']['error'] = str(e)

        return test_results
