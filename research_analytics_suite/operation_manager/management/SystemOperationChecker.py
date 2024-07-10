"""
SystemOperationChecker Module.

This module defines the SystemOperationChecker class, which is responsible for managing and checking system
operations within the research analytics suite. It ensures that necessary operations such as ConsoleOperation and
ResourceMonitorOperation are running and adds them to the sequencer if they are not present.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.operation_manager.management.OperationSequencer import OperationSequencer
from research_analytics_suite.commands.ConsoleOperation import ConsoleOperation
from research_analytics_suite.operation_manager.operations.system.ResourceMonitorOperation import \
    ResourceMonitorOperation
from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator


class SystemOperationChecker:
    """
    Class to manage and check is_loop operations.

    This class is responsible for ensuring that necessary system operations, such as ConsoleOperation and
    ResourceMonitorOperation, are running within the research analytics suite. If these operations are not
    present, it adds them to the operation sequencer.
    """

    def __init__(self, sequencer: OperationSequencer, task_creator: TaskCreator):
        """
        Initializes the SystemOperationChecker with the necessary components.

        Parameters:
        - sequencer (OperationSequencer): The sequencer that holds operations to be executed.
        - task_creator (TaskCreator): The task creator that handles task generation.
        """
        from research_analytics_suite.utils.CustomLogger import CustomLogger
        self._logger = CustomLogger()

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self._operation_control = OperationControl()
        self.op_manager = self._operation_control.operation_manager

        from research_analytics_suite.commands import CommandRegistry
        self._registry = CommandRegistry()

        self.sequencer = sequencer
        self.task_creator = task_creator

    async def check_system_operations(self) -> None:
        """
        Checks for is_loop operations and adds them to the sequencer if they are not already present.

        This method ensures that a ConsoleOperation is in progress and a ResourceMonitorOperation is running. If these
        operations are not present, they are added to the operation sequencer.
        """
        if not self._operation_control.console_operation_in_progress:
            await self.op_manager.add_operation_if_not_exists(
                operation_type=ConsoleOperation, is_loop=True, parallel=True)
            self._operation_control.console_operation_in_progress = True

        # Check if a ResourceMonitorOperation is already running
        if not any(isinstance(task, ResourceMonitorOperation) for task in self.task_creator.tasks):
            await self.op_manager.add_operation_if_not_exists(
                operation_type=ResourceMonitorOperation, is_loop=True, parallel=True)
