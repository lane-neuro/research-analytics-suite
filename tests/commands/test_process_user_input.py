import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock

from research_analytics_suite.commands.UserInputProcessor import process_user_input


@pytest_asyncio.fixture
async def setup_test_environment():
    with patch('research_analytics_suite.utils.CustomLogger', autospec=True) as mock_logger_patcher, \
            patch('research_analytics_suite.commands.CommandRegistry', autospec=True) as mock_command_registry_patcher:
        mock_logger_class = mock_logger_patcher.return_value
        mock_logger_class.error = MagicMock()
        mock_logger_class.info = MagicMock()

        mock_command_registry_class = mock_command_registry_patcher.return_value
        mock_command_registry_class.execute_command = AsyncMock(return_value="Command executed successfully")

        yield {
            'mock_logger': mock_logger_class,
            'mock_command_registry': mock_command_registry_class,
        }


class TestProcessUserInput:

    @pytest_asyncio.fixture(autouse=True)
    async def setup_teardown(self, setup_test_environment):
        self.mock_logger = setup_test_environment['mock_logger']
        self.mock_command_registry = setup_test_environment['mock_command_registry']
        yield

    @pytest.mark.asyncio
    async def test_valid_command(self):
        user_input = "valid_command arg1 arg2"
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "valid_command", runtime_id, "arg1", "arg2"
        )
        assert response == "Command executed successfully"

    @pytest.mark.asyncio
    async def test_invalid_command(self):
        user_input = ""
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_logger.error.assert_called_once()
        error_message = self.mock_logger.error.call_args[0][0]
        assert str(error_message) == "Error: Unknown command ''. Type '_help' to see available commands."
        assert response is None

    @pytest.mark.asyncio
    async def test_command_without_runtime_id(self):
        user_input = "valid_command arg1"

        response = await process_user_input(user_input)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "valid_command", None, "arg1"
        )
        assert response == "Command executed successfully"

    @pytest.mark.asyncio
    async def test_command_with_spaces_only(self):
        user_input = "   "
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_logger.error.assert_called_once()
        error_message = self.mock_logger.error.call_args[0][0]
        assert str(error_message) == "Error: Unknown command '   '. Type '_help' to see available commands."
        assert response is None

    @pytest.mark.asyncio
    async def test_command_with_special_characters(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Special command executed")

        user_input = "command !@# $%^"
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "command", runtime_id, "!@#", "$%^"
        )
        assert response == "Special command executed"

    @pytest.mark.asyncio
    async def test_command_with_unicode_characters(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Unicode command executed")

        user_input = "command 你好 世界"
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
             "command", runtime_id, "你好", "世界"
        )
        assert response == "Unicode command executed"

    @pytest.mark.asyncio
    async def test_command_with_mixed_alphanumeric(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Mixed command executed")

        user_input = "command arg1 123"
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "command", runtime_id, "arg1", "123"
        )
        assert response == "Mixed command executed"

    @pytest.mark.asyncio
    async def test_command_execution_failure(self):
        self.mock_command_registry.execute_command = AsyncMock(side_effect=Exception("Execution failed"))

        user_input = "failing_command arg1"
        runtime_id = "runtime_123"

        with pytest.raises(Exception, match="Execution failed"):
            await process_user_input(user_input, runtime_id)

    @pytest.mark.asyncio
    async def test_command_with_no_arguments(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Command with no arguments executed")

        user_input = "noarg_command"
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "noarg_command", runtime_id
        )
        assert response == "Command with no arguments executed"

    @pytest.mark.asyncio
    async def test_command_with_quoted_arguments(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Command with quoted arguments executed")

        user_input = 'command "arg with spaces" "another arg"'
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        self.mock_command_registry.execute_command.assert_called_once_with(
            "command", runtime_id, "arg with spaces", "another arg"
        )
        assert response == "Command with quoted arguments executed"

    @pytest.mark.asyncio
    async def test_long_command_with_many_arguments(self):
        self.mock_command_registry.execute_command = AsyncMock(return_value="Long command executed")

        user_input = "command " + " ".join([f"arg{i}" for i in range(100)])
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)

        expected_args = [f"arg{i}" for i in range(100)]
        self.mock_command_registry.execute_command.assert_called_once_with(
            "command", runtime_id, *expected_args
        )
        assert response == "Long command executed"

    @pytest.mark.asyncio
    async def test_non_string_input(self):
        user_input = 12345  # Non-string input
        runtime_id = "runtime_123"

        response = await process_user_input(user_input, runtime_id)
        assert response is None
