"""
Module description.

Longer description.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from neurobehavioral_analytics_suite.operation_manager.operation.persistent.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_manager.operation.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation


class PersistentOperationChecker:
    def __init__(self, operation_control, operation_manager, queue, task_manager, logger, error_handler):
        self.op_control = operation_control
        self.op_manager = operation_manager
        self.queue = queue
        self.task_manager = task_manager
        self.logger = logger
        self.error_handler = error_handler

    async def check_persistent_operations(self):
        """
        Checks for persistent operations and adds them to the queue if they are not already present.
        """

        if not self.op_control.console_operation_in_progress:
            await self.op_manager.add_operation_if_not_exists(operation_type=ConsoleOperation,
                                                              error_handler=self.error_handler,
                                                              user_input_handler=self.op_control.user_input_handler,
                                                              logger=self.logger, local_vars=self.op_control.local_vars,
                                                              name="ConsoleOperation", prompt="")
            self.op_control.console_operation_in_progress = True

        # Check if a ResourceMonitorOperation is already running
        if not any(isinstance(task, ResourceMonitorOperation) for task in self.task_manager.tasks):
            await self.op_manager.add_operation_if_not_exists(operation_type=ResourceMonitorOperation,
                                                              error_handler=self.error_handler)
