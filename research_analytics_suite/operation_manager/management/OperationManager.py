"""
OperationManager Module.

This module defines the OperationManager class, which manages the creation, queuing, and control of operations within
the research analytics suite. It provides methods to add, resume, pause, and stop operations.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from typing import Type

from research_analytics_suite.commands import command, link_class_commands
from research_analytics_suite.operation_manager.operations.system.ResourceMonitor import ResourceMonitor
from research_analytics_suite.operation_manager.operations.system.ConsoleMonitor import ConsoleMonitor
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


@link_class_commands
class OperationManager:
    """
    A class to manage operations within the research analytics suite.

    This class provides methods to add operations to the sequencer, and to resume, pause, and stop operations.
    """

    def __init__(self, sequencer, task_creator):
        """
        Initializes the OperationManager with the necessary components.

        Args:
            sequencer: Sequencer holding operations to be managed.
            task_creator: Task creator for generating asyncio tasks.
        """
        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self.op_control = OperationControl()

        self.sequencer = sequencer
        self.task_creator = task_creator
        self._logger = CustomLogger()

        self.resource_monitor = None
        self.console_monitor = None

    async def initialize(self):
        """
        Initializes the OperationManager.
        """
        self.resource_monitor = await self.create_operation(
            ResourceMonitor, cpu_threshold=90, memory_threshold=95)
        self._logger.debug("Resource monitor initialized.")
        self.console_monitor = await self.create_operation(
            ConsoleMonitor, prompt="\n\t>>\t")
        self._logger.debug("Console monitor initialized.")

    @command
    async def add_initialized_operation(self, operation: BaseOperation) -> BaseOperation:
        """
        Adds an initialized operation to the sequencer.

        Args:
            operation (BaseOperation): The initialized operation to add.
        """
        if operation is None:
            self._logger.error(Exception("Attempted to add a None operation to the sequencer."),
                               self.__class__.__name__)
            raise
        self._logger.debug(f"Adding initialized operation to sequencer: {operation.name} "
                           f"with rID: {operation.runtime_id}")
        await self.sequencer.add_operation_to_sequencer(operation)
        self._logger.debug(f"Operation {operation.name} added to sequencer.")
        operation.add_log_entry(f"[SEQ] {operation.name}")
        return operation

    @command
    async def create_operation(self, operation_type: Type[BaseOperation], *args, **kwargs) -> BaseOperation:
        """
        Creates a new Operation object with the specified parameters.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Operation: The created operation.
        """
        try:
            self._logger.debug(f"Creating operation of type: {operation_type}")
            kwargs['active'] = True
            operation = operation_type(*args, **kwargs)
            await operation.initialize_operation()
            self._logger.debug(f"Initialized operation: {operation.name} with ID: {operation.runtime_id}"
                               f" and action: {operation.action}")

            operation = await self.add_initialized_operation(operation)

            return operation
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    @command
    async def add_operation_with_parameters(
            self, operation_type: Type[BaseOperation], *args, **kwargs) -> BaseOperation:
        """
        Creates a new Operation object with the specified parameters and adds it to the sequencer.

        Args:
            operation_type: The type of operation to be created.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Operation: The created operation.
        """
        try:
            self._logger.debug(f"Creating operation of type: {operation_type.__name__}")
            kwargs['active'] = True
            operation = operation_type(*args, **kwargs)
            await operation.initialize_operation()
            self._logger.debug(f"Initialized operation: {operation.name} with ID: {operation.runtime_id}")

            if operation.parent_operation is not None:
                await operation.parent_operation.add_child_operation(operation)
                self._logger.debug(f"Added operation {operation.name} as child of {operation.parent_operation.name}")

            _operation = await self.add_initialized_operation(operation)
            return _operation
        except Exception as e:
            self._logger.error(e, self.__class__.__name__)
            raise

    @command
    async def resume_operation(self, operation: BaseOperation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (BaseOperation): The operation to resume.
        """
        if operation.status == "paused":
            await operation.resume()

    @command
    async def pause_operation(self, operation: BaseOperation) -> None:
        """
        Pauses a specific operation.

        Args:
            operation (BaseOperation): The operation to pause.
        """
        if operation.status == "running":
            await operation.pause()

    @command
    async def stop_operation(self, operation: BaseOperation, child_operations: bool = False) -> None:
        """
        Stops a specific operation.

        Args:
            operation (BaseOperation): The operation to stop.
            child_operations (bool): Flag to stop child operations as well.
        """
        await operation.stop(child_operations=child_operations)
