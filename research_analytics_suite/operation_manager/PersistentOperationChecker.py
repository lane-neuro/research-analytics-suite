"""
PersistentOperationChecker Module.

This module defines the PersistentOperationChecker class, which is responsible for managing and checking persistent
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
from research_analytics_suite.operation_manager.OperationManager import OperationManager
from research_analytics_suite.operation_manager.OperationSequencer import OperationSequencer
from research_analytics_suite.operation_manager.operations.persistent.ConsoleOperation import ConsoleOperation
from research_analytics_suite.operation_manager.operations.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation
from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator
from research_analytics_suite.utils.CustomLogger import CustomLogger


class PersistentOperationChecker:
    """
    Class to manage and check persistent operations.

    This class is responsible for ensuring that necessary persistent operations, such as ConsoleOperation and
    ResourceMonitorOperation, are running within the research analytics suite. If these operations are not
    present, it adds them to the operation sequencer.
    """

    def __init__(self, operation_manager: OperationManager, sequencer: OperationSequencer,
                 task_creator: TaskCreator):
        """
        Initializes the PersistentOperationChecker with the necessary components.

        Parameters:
        - operation_manager (OperationManager): The manager responsible for operations.
        - sequencer (OperationSequencer): The sequencer that holds operations to be executed.
        - task_creator (TaskCreator): The task creator that handles task generation.
        """
        from research_analytics_suite.operation_manager.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self.op_manager = operation_manager
        self.sequencer = sequencer
        self.task_creator = task_creator
        self._logger = CustomLogger()

    async def check_persistent_operations(self) -> None:
        """
        Checks for persistent operations and adds them to the sequencer if they are not already present.

        This method ensures that a ConsoleOperation is in progress and a ResourceMonitorOperation is running. If these
        operations are not present, they are added to the operation sequencer.
        """
        if not self._operation_control.console_operation_in_progress:
            await self.op_manager.add_operation_if_not_exists(operation_type=ConsoleOperation,
                                                              user_input_manager=self._operation_control.user_input_manager,
                                                              func=self._operation_control.user_input_manager.process_user_input,
                                                              prompt="", concurrent=True,
                                                              persistent=True)
            self._operation_control.console_operation_in_progress = True

        # Check if a ResourceMonitorOperation is already running
        if not any(isinstance(task, ResourceMonitorOperation) for task in self.task_creator.tasks):
            await self.op_manager.add_operation_if_not_exists(operation_type=ResourceMonitorOperation,
                                                              concurrent=True, persistent=True)
