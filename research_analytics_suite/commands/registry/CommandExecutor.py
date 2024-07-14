"""
CommandExecutor Module

This module defines the CommandExecutor class, which executes registered commands within the Research Analytics Suite.
It provides methods to initialize and execute commands, supporting both synchronous and asynchronous functions.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from asyncio import iscoroutinefunction

from research_analytics_suite.commands.registry.RegistrationManager import RegistrationManager
from research_analytics_suite.utils.SingletonChecker import is_singleton


class CommandExecutor:
    """Class that executes registered commands."""

    def __init__(self, registration_manager: RegistrationManager):
        """Initialize the CommandExecutor with the registration manager."""
        self._logger = None
        self._config = None
        self._operation_control = None
        self._library_manifest = None
        self._workspace = None

        self._registration_manager = registration_manager

        self._initialized = False

    async def initialize(self):
        """Initialize the CommandExecutor and its components asynchronously."""
        if not self._initialized:
            from research_analytics_suite.utils import CustomLogger
            self._logger = CustomLogger()

            from research_analytics_suite.utils import Config
            self._config = Config()

            from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
            self._operation_control = OperationControl()

            from research_analytics_suite.library_manifest import LibraryManifest
            self._library_manifest = LibraryManifest()

            from research_analytics_suite.data_engine import Workspace
            self._workspace = Workspace()

            await self._registration_manager.initialize()

            self._initialized = True

    async def execute_command(self, name, runtime_id=None, *args, **kwargs):
        """Execute a command by name.

        Args:
            name (str): The name of the command.
            runtime_id: The runtime ID for instance-specific methods.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            The result of the command execution, or None if the command is not found or if there is an error.
        """
        cmd_meta = self._registration_manager.registry.get(name)
        if cmd_meta is None:
            self._logger.error(ValueError(f"Command '{name}' not found in the registry."), self.__class__.__name__)
            return None

        if bool(cmd_meta['is_method']):
            if runtime_id is None:
                self._logger.error(ValueError("Instance-specific method requires a runtime ID."),
                                   self.__class__.__name__)
                _class = cmd_meta['class_name']
                if is_singleton(_class):
                    instance = _class()
                    _returns = cmd_meta['func'](instance, *args, **kwargs)
                    if _returns is not None:
                        return _returns
                    return
                else:
                    self._logger.error(ValueError(f"Instance with runtime ID '{runtime_id}' not found."),
                                       self.__class__.__name__)
                    return None

            instance = self._registration_manager.get_instance(runtime_id)
            if instance is None:
                self._logger.error(ValueError(f"Instance with runtime ID '{runtime_id}' not found."),
                                   self.__class__.__name__)
                return None

            if iscoroutinefunction(cmd_meta['func']):
                _returns = await cmd_meta['func'](instance, *args, **kwargs)
                if _returns is not None:
                    return _returns
                return
            else:
                _returns = cmd_meta['func'](instance, *args, **kwargs)
                if _returns is not None:
                    return _returns
                return
        else:
            expected_arg_types = [arg['type'] for arg in cmd_meta['args']]
            received_arg_types = [type(arg) for arg in args]
            if expected_arg_types != received_arg_types:
                self._logger.error(f"Command '{name}' requires arguments of type {expected_arg_types}, "
                                   f"but received {received_arg_types}.", self.__class__.__name__)
                return None

            if not cmd_meta['args']:
                if iscoroutinefunction(cmd_meta['func']):
                    _returns = await cmd_meta['func']()
                    if _returns is not None:
                        return _returns
                    return
                else:
                    _returns = cmd_meta['func']()
                    if _returns is not None:
                        return _returns
                    return
            else:
                if iscoroutinefunction(cmd_meta['func']):
                    _returns = await cmd_meta['func'](*args, **kwargs)
                    if _returns is not None:
                        return _returns
                    return
                else:
                    _returns = cmd_meta['func'](*args, **kwargs)
                    if _returns is not None:
                        return _returns
                    return
