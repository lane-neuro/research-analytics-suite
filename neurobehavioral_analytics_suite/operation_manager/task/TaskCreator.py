"""
TaskCreator Module.

This module defines the TaskCreator class responsible for creating and scheduling tasks within the Neurobehavioral
AnalyticsCore Suite. It handles task creation and tracking.

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
from neurobehavioral_analytics_suite.operation_manager.task.TaskCounter import TaskCounter


class TaskCreator:
    """Handles the creation and scheduling of tasks."""

    def __init__(self, queue, logger):
        """
        Initializes the TaskCreator with the given logger.

        Args:
            logger: Logger for task-related logs.
        """
        self.task_counter = TaskCounter(logger)
        self.queue = queue
        self.logger = logger

        self.tasks = set()

    def task_exists(self, operation_type):
        """
        Checks if a task of the specified operations type exists and is running or started.

        Args:
            operation_type: The type of operations to check for.

        Returns:
            bool: True if a task of the specified type exists and is running or started, otherwise False.
        """
        return (any(isinstance(task, operation_type) and task.status in ["running", "started"] for task in self.tasks)
                or any(isinstance(operation_chain.head.operation, operation_type) for operation_chain in
                       self.queue.queue))

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
