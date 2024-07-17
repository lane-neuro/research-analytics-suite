from research_analytics_suite.operation_manager.operations.core.workspace import pack_for_save


class MockOperation:
    def __init__(self, name, version, description, category_id, author, github, email, unique_id, action,
                 required_inputs=None, parent_operation=None, inheritance=None, is_loop=False, is_cpu_bound=False,
                 parallel=False):
        self.name = name
        self.version = version
        self.description = description
        self.category_id = category_id
        self.author = author
        self.github = github
        self.email = email
        self.unique_id = unique_id
        self.action = action
        self.required_inputs = required_inputs
        self.parent_operation = parent_operation
        self.inheritance = inheritance
        self.is_loop = is_loop
        self.is_cpu_bound = is_cpu_bound
        self.parallel = parallel


class TestPackForSave:

    def setup_method(self):
        """Setup any state specific to the execution of the given module."""
        self.parent_operation = MockOperation(
            name="Parent Operation",
            version="1.0.1",
            description="A parent operation for testing",
            category_id="cat124",
            author="Parent Author",
            github="https://github.com/parent/repo",
            email="parent@example.com",
            unique_id="unique124",
            action="parent_action"
        )

        self.child_operation = MockOperation(
            name="Child Operation",
            version="1.0.2",
            description="A child operation for testing",
            category_id="cat125",
            author="Child Author",
            github="https://github.com/child/repo",
            email="child@example.com",
            unique_id="unique125",
            action="child_action"
        )

        self.operation = MockOperation(
            name="Sample Operation",
            version="1.0.0",
            description="A sample operation for testing",
            category_id="cat123",
            author="Author Name",
            github="https://github.com/sample/repo",
            email="sample@example.com",
            unique_id="unique123",
            action="sample_action",
            required_inputs={"input1": "value1"},
            parent_operation=self.parent_operation,
            inheritance=[self.child_operation],
            is_loop=True,
            is_cpu_bound=True,
            parallel=True
        )

    def test_pack_for_save(self):
        """Test the pack_for_save function with a standard operation."""
        result = pack_for_save(self.operation)
        expected = {
            'name': "Sample Operation",
            'version': "1.0.0",
            'description': "A sample operation for testing",
            'category_id': "cat123",
            'author': "Author Name",
            'github': "https://github.com/sample/repo",
            'email': "sample@example.com",
            'unique_id': "unique123",
            'action': "sample_action",
            'required_inputs': {"input1": "value1"},
            'parent_operation': {
                'name': "Parent Operation",
                'version': "1.0.1",
                'description': "A parent operation for testing",
                'category_id': "cat124",
                'author': "Parent Author",
                'github': "https://github.com/parent/repo",
                'unique_id': "unique124"
            },
            'inheritance': [{
                'name': "Child Operation",
                'version': "1.0.2",
                'description': "A child operation for testing",
                'category_id': "cat125",
                'author': "Child Author",
                'github': "https://github.com/child/repo",
                'unique_id': "unique125"
            }],
            'is_loop': True,
            'is_cpu_bound': True,
            'parallel': True,
        }
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_empty_operation(self):
        """Test the pack_for_save function with an operation having empty fields."""
        empty_operation = MockOperation(
            name="",
            version="",
            description="",
            category_id="",
            author="",
            github="",
            email="",
            unique_id="",
            action="",
            required_inputs={},
            parent_operation=None,
            inheritance=[],
            is_loop=False,
            is_cpu_bound=False,
            parallel=False
        )
        result = pack_for_save(empty_operation)
        expected = {
            'name': "",
            'version': "",
            'description': "",
            'category_id': "",
            'author': "",
            'github': "",
            'email': "",
            'unique_id': "",
            'action': "",
            'required_inputs': {},
            'parent_operation': None,
            'inheritance': [],
            'is_loop': False,
            'is_cpu_bound': False,
            'parallel': False,
        }
        assert result == expected, f"Expected {expected}, but got {result}"

    def test_none_fields(self):
        """Test the pack_for_save function with an operation having None fields."""
        none_operation = MockOperation(
            name=None,
            version=None,
            description=None,
            category_id=None,
            author=None,
            github=None,
            email=None,
            unique_id=None,
            action=None,
            required_inputs=None,
            parent_operation=None,
            inheritance=None,
            is_loop=None,
            is_cpu_bound=None,
            parallel=None
        )
        result = pack_for_save(none_operation)
        expected = {
            'name': None,
            'version': None,
            'description': None,
            'category_id': None,
            'author': None,
            'github': None,
            'email': None,
            'unique_id': None,
            'action': None,
            'required_inputs': {},
            'parent_operation': None,
            'inheritance': [],
            'is_loop': None,
            'is_cpu_bound': None,
            'parallel': None,
        }
        assert result == expected, f"Expected {expected}, but got {result}"
