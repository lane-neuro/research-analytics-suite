"""
Comprehensive test suite for StorageLayer.py

Tests cover:
- Backend registration and management
- File operations (exists, read, write, delete)
- Directory operations (create, list, sync)
- Path routing and backend selection
- Cross-backend operations (copy, move)
- Streaming operations
- Storage statistics and metadata
- Temporary file management
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from pathlib import Path
import tempfile
import os

from research_analytics_suite.data_engine.storage.StorageLayer import StorageLayer
from research_analytics_suite.data_engine.storage.StorageBackend import (
    StorageBackend, LocalFileSystem, InMemoryStorage, TemporaryStorage
)


class TestStorageLayer:
    """Test suite for StorageLayer class"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        with patch('research_analytics_suite.utils.CustomLogger') as MockLogger:
            self.mock_logger = MagicMock()
            self.mock_logger.error = MagicMock()
            self.mock_logger.debug = MagicMock()
            self.mock_logger.info = MagicMock()
            self.mock_logger.warning = MagicMock()
            MockLogger.return_value = self.mock_logger

            self.storage_layer = StorageLayer()

            yield

    # ========================
    # Initialization Tests
    # ========================

    def test_initialization(self):
        """Test storage layer initialization"""
        assert self.storage_layer is not None
        assert self.storage_layer._backends is not None
        assert self.storage_layer._default_backend is not None

    def test_builtin_backends_registered(self):
        """Test that built-in backends are registered"""
        backends = self.storage_layer.list_backends()

        assert 'file' in backends
        assert 'memory' in backends
        assert 'temp' in backends

    def test_default_backend_is_local_filesystem(self):
        """Test that default backend is local filesystem"""
        assert self.storage_layer._default_backend.scheme == 'file'

    # ========================
    # Backend Management Tests
    # ========================

    def test_register_backend(self):
        """Test registering a new backend"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "s3"
        mock_backend.name = "S3 Storage"

        self.storage_layer.register_backend(mock_backend)

        assert "s3" in self.storage_layer._backends
        assert self.storage_layer._backends["s3"] == mock_backend

    def test_unregister_backend_success(self):
        """Test unregistering an existing backend"""
        result = self.storage_layer.unregister_backend("temp")

        assert result is True
        assert "temp" not in self.storage_layer._backends

    def test_unregister_backend_not_found(self):
        """Test unregistering non-existent backend"""
        result = self.storage_layer.unregister_backend("nonexistent")

        assert result is False

    def test_list_backends(self):
        """Test listing registered backends"""
        backends = self.storage_layer.list_backends()

        assert isinstance(backends, dict)
        assert len(backends) >= 3  # At least file, memory, temp
        assert all(isinstance(k, str) and isinstance(v, str) for k, v in backends.items())

    def test_get_backend_for_file_path(self):
        """Test getting backend for file:// path"""
        backend = self.storage_layer.get_backend("file:///test/path")

        assert backend is not None
        assert backend.scheme == "file"

    def test_get_backend_for_simple_path(self):
        """Test getting backend for simple path"""
        backend = self.storage_layer.get_backend("/test/path")

        assert backend is not None
        assert backend.scheme == "file"

    def test_get_backend_for_memory_path(self):
        """Test getting backend for memory:// path"""
        backend = self.storage_layer.get_backend("memory://data/file.txt")

        assert backend is not None
        assert backend.scheme == "memory"

    def test_get_backend_for_temp_path(self):
        """Test getting backend for temp:// path"""
        backend = self.storage_layer.get_backend("temp://file.txt")

        assert backend is not None
        assert backend.scheme == "temp"

    def test_get_backend_unknown_scheme_uses_default(self):
        """Test that unknown scheme uses default backend"""
        backend = self.storage_layer.get_backend("unknown://path")

        assert backend == self.storage_layer._default_backend

    def test_get_backend_no_default_raises_error(self):
        """Test error when no default backend and unknown scheme"""
        self.storage_layer._default_backend = None

        with pytest.raises(ValueError, match="No storage backend found"):
            self.storage_layer.get_backend("unknown://path")

    def test_get_backend_stats(self):
        """Test getting backend statistics"""
        stats = self.storage_layer.get_backend_stats()

        assert 'total_backends' in stats
        assert 'backends' in stats
        assert 'default_backend' in stats
        assert stats['total_backends'] >= 3
        assert isinstance(stats['backends'], dict)

    # ========================
    # File Operation Tests
    # ========================

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test checking if path exists"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.exists = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.exists("test://file.txt")

        assert result is True
        mock_backend.exists.assert_called_once_with("test://file.txt")

    @pytest.mark.asyncio
    async def test_is_file(self):
        """Test checking if path is a file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.is_file = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.is_file("test://file.txt")

        assert result is True
        mock_backend.is_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_directory(self):
        """Test checking if path is a directory"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.is_directory = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.is_directory("test://dir")

        assert result is True
        mock_backend.is_directory.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_size(self):
        """Test getting file size"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.get_size = AsyncMock(return_value=12345)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.get_size("test://file.txt")

        assert result == 12345

    @pytest.mark.asyncio
    async def test_list_files(self):
        """Test listing files"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.list_files = AsyncMock(return_value=["file1.txt", "file2.txt"])

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.list_files("test://dir", "*.txt")

        assert len(result) == 2
        assert "file1.txt" in result
        mock_backend.list_files.assert_called_once_with("test://dir", "*.txt")

    @pytest.mark.asyncio
    async def test_read_bytes(self):
        """Test reading bytes from file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.read_bytes = AsyncMock(return_value=b"test data")

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.read_bytes("test://file.txt")

        assert result == b"test data"
        mock_backend.read_bytes.assert_called_once_with("test://file.txt", 0, None)

    @pytest.mark.asyncio
    async def test_read_bytes_with_range(self):
        """Test reading bytes with start and length"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.read_bytes = AsyncMock(return_value=b"data")

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.read_bytes("test://file.txt", start=10, length=100)

        assert result == b"data"
        mock_backend.read_bytes.assert_called_once_with("test://file.txt", 10, 100)

    @pytest.mark.asyncio
    async def test_read_text(self):
        """Test reading text from file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.read_text = AsyncMock(return_value="test content")

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.read_text("test://file.txt")

        assert result == "test content"
        mock_backend.read_text.assert_called_once_with("test://file.txt", 'utf-8')

    @pytest.mark.asyncio
    async def test_read_text_custom_encoding(self):
        """Test reading text with custom encoding"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.read_text = AsyncMock(return_value="test")

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.read_text("test://file.txt", encoding="utf-16")

        mock_backend.read_text.assert_called_once_with("test://file.txt", "utf-16")

    @pytest.mark.asyncio
    async def test_write_bytes(self):
        """Test writing bytes to file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.write_bytes = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.write_bytes("test://file.txt", b"data")

        assert result is True
        mock_backend.write_bytes.assert_called_once_with("test://file.txt", b"data", False)

    @pytest.mark.asyncio
    async def test_write_bytes_append(self):
        """Test writing bytes with append"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.write_bytes = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.write_bytes("test://file.txt", b"data", append=True)

        assert result is True
        mock_backend.write_bytes.assert_called_once_with("test://file.txt", b"data", True)

    @pytest.mark.asyncio
    async def test_write_text(self):
        """Test writing text to file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.write_text = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.write_text("test://file.txt", "content")

        assert result is True
        mock_backend.write_text.assert_called_once_with("test://file.txt", "content", 'utf-8', False)

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test deleting a file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.delete = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.delete("test://file.txt")

        assert result is True
        mock_backend.delete.assert_called_once()

    # ========================
    # Copy/Move Tests
    # ========================

    @pytest.mark.asyncio
    async def test_copy_same_backend(self):
        """Test copying within same backend"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.copy = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.copy("test://source.txt", "test://dest.txt")

        assert result is True
        mock_backend.copy.assert_called_once_with("test://source.txt", "test://dest.txt")

    @pytest.mark.asyncio
    async def test_copy_cross_backend(self):
        """Test copying across different backends"""
        source_backend = MagicMock(spec=StorageBackend)
        source_backend.scheme = "source"

        dest_backend = MagicMock(spec=StorageBackend)
        dest_backend.scheme = "dest"
        dest_backend.sync_from = AsyncMock(return_value=True)

        self.storage_layer.register_backend(source_backend)
        self.storage_layer.register_backend(dest_backend)

        result = await self.storage_layer.copy("source://file.txt", "dest://file.txt")

        assert result is True
        dest_backend.sync_from.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_success(self):
        """Test moving a file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.copy = AsyncMock(return_value=True)
        mock_backend.delete = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.move("test://source.txt", "test://dest.txt")

        assert result is True
        mock_backend.copy.assert_called_once()
        mock_backend.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_move_copy_fails(self):
        """Test move when copy fails"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.copy = AsyncMock(return_value=False)
        mock_backend.delete = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.move("test://source.txt", "test://dest.txt")

        assert result is False
        mock_backend.delete.assert_not_called()

    # ========================
    # Directory Tests
    # ========================

    @pytest.mark.asyncio
    async def test_create_directory(self):
        """Test creating a directory"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.create_directory = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.create_directory("test://newdir")

        assert result is True
        mock_backend.create_directory.assert_called_once()

    # ========================
    # Metadata Tests
    # ========================

    @pytest.mark.asyncio
    async def test_get_metadata(self):
        """Test getting file metadata"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.name = "Test Backend"
        mock_backend.get_metadata = AsyncMock(return_value={'size': 123, 'modified': 'timestamp'})

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.get_metadata("test://file.txt")

        assert 'size' in result
        assert 'backend' in result
        assert 'scheme' in result
        assert result['backend'] == "Test Backend"
        assert result['scheme'] == "test"

    # ========================
    # Streaming Tests
    # ========================

    @pytest.mark.asyncio
    async def test_stream_read(self):
        """Test streaming file read"""
        async def mock_stream(path, chunk_size):
            yield b"chunk1"
            yield b"chunk2"
            yield b"chunk3"

        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.stream_read = mock_stream

        self.storage_layer.register_backend(mock_backend)

        chunks = []
        async for chunk in self.storage_layer.stream_read("test://file.txt"):
            chunks.append(chunk)

        assert len(chunks) == 3
        assert chunks[0] == b"chunk1"
        assert chunks[2] == b"chunk3"

    # ========================
    # File Finding Tests
    # ========================

    @pytest.mark.asyncio
    async def test_find_files_recursive(self):
        """Test finding files recursively"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.list_files = AsyncMock(return_value=["file1.txt", "sub/file2.txt"])

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.find_files("test://dir", "*.txt", recursive=True)

        assert len(result) == 2
        mock_backend.list_files.assert_called_once_with("test://dir", "**/*.txt")

    @pytest.mark.asyncio
    async def test_find_files_non_recursive(self):
        """Test finding files non-recursively"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.list_files = AsyncMock(return_value=["file1.txt"])

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.find_files("test://dir", "*.txt", recursive=False)

        assert len(result) == 1
        mock_backend.list_files.assert_called_once_with("test://dir", "*.txt")

    @pytest.mark.asyncio
    async def test_find_files_error_handling(self):
        """Test find files error handling"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.list_files = AsyncMock(side_effect=Exception("Read error"))

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.find_files("test://dir", "*.txt")

        # Should return empty list on error
        assert result == []
        # Error message was printed to stdout (we can see it in captured output)

    # ========================
    # Temporary File Tests
    # ========================

    def test_get_temp_path_with_filename(self):
        """Test getting temporary path with filename"""
        path = self.storage_layer.get_temp_path("test.txt")

        assert "temp://" in path
        assert "test.txt" in path

    def test_get_temp_path_without_filename(self):
        """Test getting temporary path without filename"""
        path = self.storage_layer.get_temp_path()

        assert "temp://" in path
        assert len(path) > len("temp://data/")

    def test_get_temp_path_no_temp_backend(self):
        """Test getting temp path when temp backend not available"""
        self.storage_layer.unregister_backend("temp")

        path = self.storage_layer.get_temp_path("test.txt")

        # Should fall back to system temp
        assert "temp://" not in path

    @pytest.mark.asyncio
    async def test_create_temp_file(self):
        """Test creating temporary file"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "temp"
        mock_backend.write_bytes = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.create_temp_file(b"test content", "test.txt")

        assert "temp://" in result
        mock_backend.write_bytes.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_temp_storage(self):
        """Test cleaning up temporary storage"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "temp"
        mock_backend.cleanup = MagicMock()

        self.storage_layer.register_backend(mock_backend)

        await self.storage_layer.cleanup_temp_storage()

        mock_backend.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_temp_storage_no_cleanup_method(self):
        """Test cleanup when backend has no cleanup method"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "temp"
        delattr(mock_backend, 'cleanup')  # Remove cleanup method

        self.storage_layer.register_backend(mock_backend)

        # Should not raise exception
        await self.storage_layer.cleanup_temp_storage()

    # ========================
    # Backend Testing Tests
    # ========================

    @pytest.mark.asyncio
    async def test_test_backend_success(self):
        """Test backend testing functionality"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.name = "Test Backend"
        mock_backend.write_bytes = AsyncMock(return_value=True)
        mock_backend.read_bytes = AsyncMock(return_value=b"Hello, World!")
        mock_backend.exists = AsyncMock(return_value=True)
        mock_backend.delete = AsyncMock(return_value=True)

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.test_backend("test")

        assert result['backend'] == "Test Backend"
        assert result['scheme'] == "test"
        assert 'tests' in result
        assert result['tests']['write'] is True
        assert result['tests']['read'] is True
        assert result['tests']['exists'] is True
        assert result['tests']['delete'] is True

    @pytest.mark.asyncio
    async def test_test_backend_not_found(self):
        """Test testing non-existent backend"""
        result = await self.storage_layer.test_backend("nonexistent")

        assert 'error' in result
        assert 'not found' in result['error']

    @pytest.mark.asyncio
    async def test_test_backend_with_error(self):
        """Test backend testing when operation fails"""
        mock_backend = MagicMock(spec=StorageBackend)
        mock_backend.scheme = "test"
        mock_backend.name = "Test Backend"
        mock_backend.write_bytes = AsyncMock(side_effect=Exception("Write failed"))

        self.storage_layer.register_backend(mock_backend)

        result = await self.storage_layer.test_backend("test")

        assert 'tests' in result
        assert 'error' in result['tests']
