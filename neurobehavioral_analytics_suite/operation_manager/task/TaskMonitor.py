"""
TaskMonitor Module.

This module defines the TaskMonitor class responsible for monitoring and managing tasks within the Neurobehavioral
Analytics Suite. It handles task monitoring and completion.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

from neurobehavioral_analytics_suite.operation_manager.operations.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_manager.operations.computation.DaskOperation import DaskOperation
from neurobehavioral_analytics_suite.operation_manager.operations.persistent.ConsoleOperation import ConsoleOperation


class TaskMonitor:
    """Monitors and manages tasks."""

    def __init__(self, task_creator, queue, logger, error_handler):
        """
        Initializes the TaskMonitor with the given parameters.

        Args:
            task_creator: The task creator.
            queue: The operations queue.
            logger: Logger for task-related logs.
            error_handler: Handler for managing errors.
        """
        self.task_creator = task_creator
        self.queue = queue
        self.logger = logger
        self.error_handler = error_handler

    async def handle_tasks(self):
        """Handles the execution and monitoring of tasks."""
        self.logger.debug("handle_tasks: [INIT]")
        for task in self.task_creator.tasks.copy():
            self.logger.debug(f"handle_tasks: [CHECK] {task.get_name()}")
            if task.done():
                operation = self.queue.find_operation_by_task(task)
                try:
                    self.logger.debug(f"handle_tasks: [OP] {task.get_name()}")
                    if operation is not None:
                        await operation.task
                        if isinstance(operation, CustomOperation):
                            output = operation.result_output
                            self.queue.local_vars = output
                            self.logger.info(f"handle_tasks: [OUTPUT] {output}")
                        elif isinstance(operation, DaskOperation):
                            output = operation.result
                            self.logger.info(f"handle_tasks: [OUTPUT] {output}")

                        self.logger.info(f"handle_tasks: [DONE] {task.get_name()}")
                    else:
                        self.logger.error(f"handle_tasks: [ERROR] No operations found for task {task.get_name()}")
                except Exception as e:
                    self.error_handler.handle_error(e, self)
                finally:
                    if operation:
                        self.task_creator.tasks.remove(task)
                        if not operation.persistent:
                            self.queue.remove_operation_from_queue(operation)

                        if isinstance(operation, ConsoleOperation):
                            self.queue.console_operation_in_progress = False
