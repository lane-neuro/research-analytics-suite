import pytest
import os
from unittest import mock
from research_analytics_suite.data_engine.data_streams.DataTypeDetector import read_partial_file


class TestReadPartialFile:
    def test_read_partial_text_file(self, tmp_path):
        # Create a temporary text file
        file_path = tmp_path / "test.txt"
        content = "Hello, this is a test file."
        file_path.write_text(content)

        # Test reading part of the file
        result = read_partial_file(str(file_path), 5)
        assert result == "Hello"

    def test_read_partial_binary_file(self, tmp_path):
        # Create a temporary binary file
        file_path = tmp_path / "test.bin"
        content = b"Hello, this is a binary file."
        file_path.write_bytes(content)

        # Test reading part of the binary file
        result = read_partial_file(str(file_path), 5, binary=True)
        assert result == b"Hello"

    def test_read_partial_text_file_with_unicode(self, tmp_path):
        # Create a temporary text file with unicode content
        file_path = tmp_path / "test_unicode.txt"
        content = "Hello, this is a test file with unicode: 測試文件"
        file_path.write_text(content, encoding='utf-8')

        # Test reading part of the file with unicode
        result = read_partial_file(str(file_path), 30)  # Adjust size to match character count
        assert result == "Hello, this is a test file wit"

    def test_read_partial_binary_file_with_unicode(self, tmp_path):
        # Create a temporary binary file with unicode content
        file_path = tmp_path / "test_unicode.bin"
        content = "Hello, this is a test file with unicode: 測試文件".encode('utf-8')
        file_path.write_bytes(content)

        # Test reading part of the binary file with unicode
        result = read_partial_file(str(file_path), 29, binary=True)
        assert result == content[:29]

    def test_read_empty_file(self, tmp_path):
        # Create a temporary empty file
        file_path = tmp_path / "empty.txt"
        file_path.write_text("")

        # Test reading from an empty file
        result = read_partial_file(str(file_path), 10)
        assert result == ""

    def test_read_partial_file_size_larger_than_content(self, tmp_path):
        # Create a temporary text file
        file_path = tmp_path / "small.txt"
        content = "Small file"
        file_path.write_text(content)

        # Test reading more bytes than available in the file
        result = read_partial_file(str(file_path), 20)
        assert result == content

    def test_read_partial_binary_file_size_larger_than_content(self, tmp_path):
        # Create a temporary binary file
        file_path = tmp_path / "small.bin"
        content = b"Small binary file"
        file_path.write_bytes(content)

        # Test reading more bytes than available in the binary file
        result = read_partial_file(str(file_path), 20, binary=True)
        assert result == content

    def test_read_partial_file_non_existent(self):
        # Test reading from a non-existent file
        with pytest.raises(FileNotFoundError):
            read_partial_file("non_existent.txt", 10)

    def test_read_partial_file_permission_denied(self, tmp_path):
        # Create a temporary file
        file_path = tmp_path / "permission_denied.txt"
        file_path.write_text("This file cannot be read.")

        # Simulate PermissionError when opening the file
        with mock.patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError) as exc_info:
                read_partial_file(str(file_path), 10)
            assert "Permission denied" in str(exc_info.value)

    def test_read_partial_file_unicode_decode_error(self, tmp_path):
        # Create a temporary file with invalid UTF-8 content
        file_path = tmp_path / "invalid_utf8.txt"
        file_path.write_bytes(b"\x80\x81\x82\x83")

        # Test reading from a file with invalid UTF-8 content
        result = read_partial_file(str(file_path), 10)
        assert result == b"\x80\x81\x82\x83"
