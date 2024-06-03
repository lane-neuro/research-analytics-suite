"""
Task Manager Module.

This module defines the TaskManager class responsible for managing and executing tasks within
the Neurobehavioral Analytics Suite. The TaskManager handles the creation, monitoring, and completion
of tasks, integrating with various operations and logging mechanisms.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
from neurobehavioral_analytics_suite.operation_manager.TaskCounter import TaskCounter
from neurobehavioral_analytics_suite.operation_manager.operation.persistent.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_manager.operation.CustomOperation import CustomOperation


class TaskManager:
    """
    Manages tasks within the Neurobehavioral Analytics Suite.

    Attributes:
        task_counter (TaskCounter): Tracks and counts tasks.
        operation_control: Controls and manages operations.
        tasks (set): A set of current tasks.
        error_handler: Handles errors during task execution.
        logger: Logger for logging task-related information.
        queue: Manages the queue of operations.
    """

    def __init__(self, operation_control, logger, error_handler, queue):
        """
        Initializes the TaskManager with the given parameters.

        Args:
            operation_control: The control mechanism for operations.
            logger: Logger for task-related logs.
            error_handler: Handler for managing errors.
            queue: Queue that manages the operations.
        """
        self.task_counter = TaskCounter(logger)
        self.operation_control = operation_control
        self.tasks = set()
        self.error_handler = error_handler
        self.logger = logger
        self.queue = queue

    async def create_task(self, coro, name):
        """
        Creates and schedules a new asynchronous task.

        Args:
            coro: The coroutine to be executed as a task.
            name (str): The name of the task.

        Returns:
            asyncio.Task: The created task.
        """
        task = asyncio.create_task(coro, name=self.task_counter.new_task(name))
        self.tasks.add(task)
        return task

    def task_exists(self, operation_type):
        """
        Checks if a task of the specified operation type exists and is running or started.

        Args:
            operation_type: The type of operation to check for.

        Returns:
            bool: True if a task of the specified type exists and is running or started, otherwise False.
        """
        return (any(isinstance(task, operation_type) and task.status in ["running", "started"] for task in self.tasks)
                or any(isinstance(operation_chain.head.operation, operation_type) for operation_chain in
                       self.queue.queue))

    async def handle_tasks(self):
        """
        Handles the execution and monitoring of tasks.

        Iterates through all tasks, checking their status, handling their completion, and logging relevant information.
        """
        self.logger.debug("handle_tasks: [INIT]")
        for task in self.tasks.copy():
            self.logger.debug(f"handle_tasks: [CHECK] {task.get_name()}")
            if task.done():
                operation = self.queue.find_operation_by_task(task)
                try:
                    self.logger.debug(f"handle_tasks: [OP] {task.get_name()}")
                    if operation is not None:
                        await operation.task
                        if isinstance(operation, CustomOperation):
                            output = operation.result_output
                            self.operation_control.local_vars = output
                            self.logger.info(f"handle_tasks: [OUTPUT] {output}")
                        self.logger.info(f"handle_tasks: [DONE] {task.get_name()}")
                    else:
                        self.logger.error(f"handle_tasks: [ERROR] No operation found for task {task.get_name()}")
                except Exception as e:
                    self.error_handler.handle_error(e, self)
                finally:
                    if operation:
                        self.tasks.remove(task)
                        if not operation.persistent:
                            self.queue.remove_operation_from_queue(operation)

                        if isinstance(operation, ConsoleOperation):
                            self.operation_control.console_operation_in_progress = False
