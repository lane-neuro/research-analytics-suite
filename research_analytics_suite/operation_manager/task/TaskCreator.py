"""
TaskCreator Module.

This module defines the TaskCreator class responsible for creating and scheduling tasks within the Neurobehavioral
Analytics Suite. It handles task creation and tracking.

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

from research_analytics_suite.operation_manager.task.TaskCounter import TaskCounter
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TaskCreator:
    """Handles the creation and scheduling of tasks."""

    def __init__(self, sequencer):
        """
        Initializes the TaskCreator with the given logger.

        Args:
            sequencer: The sequencer to which tasks are added.
        """
        self.task_counter = TaskCounter()
        self.sequencer = sequencer
        self._logger = CustomLogger()

        self.tasks = set()

    def task_exists(self, runtime_id) -> bool:
        """
        Checks if a task with the given runtime ID exists.

        Args:
            runtime_id (str): The runtime ID to check.

        Returns:
            bool: True if a task of the specified type exists and is running or started, otherwise False.
        """
        for task in self.tasks:
            _name = task.get_name().split(']')[1]
            if _name == runtime_id:
                return True
        return False

    def create_task(self, coro, name):
        """
        Creates and schedules a new asynchronous task.

        Args:
            coro: The coroutine to be executed as a task.
            name (str): The name of the task.

        Returns:
            asyncio.Task: The created task.
        """
        task_name = self.task_counter.new_task(name)
        task = asyncio.create_task(coro, name=task_name)
        self.tasks.add(task)
        self._logger.debug(f"Task {task_name} created.")
        return task

    def cancel_task(self, task_name):
        """
        Cancels a task by its name.

        Args:
            task_name (str): The name of the task to cancel.

        Returns:
            bool: True if the task was found and cancelled, False otherwise.
        """
        for task in self.tasks:
            _name = task.get_name().split(']')[1]
            if _name == task_name:
                task.cancel()
                self.tasks.remove(task)
                self._logger.info(f"Task {task_name} cancelled.")
                return True
        return False

