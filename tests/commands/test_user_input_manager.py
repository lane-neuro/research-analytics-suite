import pytest
from unittest.mock import AsyncMock, Mock, patch
from research_analytics_suite.commands.UserInputManager import UserInputManager
from research_analytics_suite.commands import CommandRegistry


class TestUserInputManager:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Initialize the UserInputManager instance
        self.user_input_manager = UserInputManager()

        # Mock dependencies
        self.user_input_manager._operation_control = Mock()
        self.user_input_manager._logger = Mock()

        # Get the singleton instance and reset its state
        self.command_registry = CommandRegistry()
        self.command_registry._registry = {}

        # Patch the imports in UserInputManager
        patcher1 = patch('research_analytics_suite.operation_manager.control.OperationControl',
                         return_value=self.user_input_manager._operation_control)
        patcher2 = patch('research_analytics_suite.utils.CustomLogger',
                         return_value=self.user_input_manager._logger)

        patcher1.start()
        patcher2.start()

        yield

        patcher1.stop()
        patcher2.stop()

    @pytest.mark.asyncio
    async def test_process_user_input_known_command_no_class(self):
        # Setup the command registry mock
        self.command_registry._registry = {
            'test_command': {
                'func': Mock(return_value='command executed'),
                'name': 'test_command',
                'class_name': None,
                'args': [{'name': 'arg1', 'type': str}],
                'return_type': 'str',
                'is_method': False
            }
        }

        # Test process_user_input with a known command
        result = await self.user_input_manager.process_user_input('test_command arg1_value')
        assert result == 'command executed'

    @pytest.mark.asyncio
    async def test_process_user_input_unknown_command(self):
        # Test process_user_input with an unknown command
        result = await self.user_input_manager.process_user_input('unknown_command')
        assert result == "Error: Unknown command \'unknown_command\'. Type 'ras_help' to see available commands."

    @pytest.mark.asyncio
    async def test_execute_command_with_correct_args(self):
        # Setup the command registry mock
        self.command_registry._registry = {
            'test_command': {
                'func': Mock(return_value='command executed'),
                'name': 'test_command',
                'class_name': None,
                'args': [{'name': 'arg1', 'type': str}],
                'return_type': 'str',
                'is_method': False
            }
        }

        # Test execute_command with correct arguments
        result = await self.user_input_manager.execute_command('test_command', ['arg1_value'])
        assert result == 'command executed'

    @pytest.mark.asyncio
    async def test_execute_command_with_incorrect_args(self):
        # Setup the command registry mock
        self.command_registry._registry = {
            'test_command': {
                'func': Mock(return_value='command executed'),
                'name': 'test_command',
                'class_name': None,
                'args': [{'name': 'arg1', 'type': str}],
                'return_type': 'str',
                'is_method': False
            }
        }

        # Test execute_command with incorrect arguments
        result = await self.user_input_manager.execute_command('test_command', [])
        assert result == 'Error: test_command expects 1 arguments but got 0.'

    @pytest.mark.asyncio
    async def test_execute_command_with_exception(self):
        # Setup the command registry mock
        self.command_registry._registry = {
            'test_command': {
                'func': AsyncMock(side_effect=Exception('Error executing command')),
                'name': 'test_command',
                'class_name': None,
                'args': [{'name': 'arg1', 'type': str}],
                'return_type': 'str',
                'is_method': False
            }
        }

        # Test execute_command which raises an exception
        result = await self.user_input_manager.execute_command('test_command', ['arg1_value'])
        assert 'Error executing command' in result

    def test_parse_command(self):
        # Test parse_command with valid input
        command_name, args = self.user_input_manager.parse_command('test_command arg1_value')
        assert command_name == 'test_command'
        assert args == ['arg1_value']

        # Test parse_command with empty input
        command_name, args = self.user_input_manager.parse_command('')
        assert command_name is None
        assert args == []

        # Test parse_command with only spaces
        command_name, args = self.user_input_manager.parse_command('   ')
        assert command_name is None
        assert args == []

