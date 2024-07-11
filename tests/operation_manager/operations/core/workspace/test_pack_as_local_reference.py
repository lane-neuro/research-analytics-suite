import pytest

from research_analytics_suite.operation_manager.operations.core.workspace import pack_as_local_reference


class MockOperation:
    def __init__(self, name, version, description, category_id, author, github, unique_id):
        self.name = name
        self.version = version
        self.description = description
        self.category_id = category_id
        self.author = author
        self.github = github
        self.unique_id = unique_id


class TestPackAsLocalReference:

    def setup_method(self):
        """Setup any state specific to the execution of the given module."""
        self.operation = MockOperation(
            name="Sample Operation",
            version="1.0.0",
            description="A sample operation for testing",
            category_id="cat123",
            author="Author Name",
            github="https://github.com/sample/repo",
            unique_id="unique123"
        )

    def test_pack_as_local_reference(self):
        """Test the pack_as_local_reference function with a standard operation."""
        result = pack_as_local_reference(self.operation)
        expected = {
            'name': "Sample Operation",
            'version': "1.0.0",
            'description': "A sample operation for testing",
            'category_id': "cat123",
            'author': "Author Name",
            'github': "https://github.com/sample/repo",
            'unique_id': "unique123",
        }
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_empty_operation(self):
        """Test the pack_as_local_reference function with an operation having empty fields."""
        empty_operation = MockOperation(
            name="",
            version="",
            description="",
            category_id="",
            author="",
            github="",
            unique_id=""
        )
        result = pack_as_local_reference(empty_operation)
        expected = {
            'name': "",
            'version': "",
            'description': "",
            'category_id': "",
            'author': "",
            'github': "",
            'unique_id': "",
        }
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_none_fields(self):
        """Test the pack_as_local_reference function with an operation having None fields."""
        none_operation = MockOperation(
            name=None,
            version=None,
            description=None,
            category_id=None,
            author=None,
            github=None,
            unique_id=None
        )
        result = pack_as_local_reference(none_operation)
        expected = {
            'name': None,
            'version': None,
            'description': None,
            'category_id': None,
            'author': None,
            'github': None,
            'unique_id': None,
        }
        assert result == expected, f"Expected {expected}, but got {result}"
