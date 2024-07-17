"""
TaskCounter Module.

This module defines the TaskCounter class, which is responsible for managing and counting tasks within a given context.
It includes methods to create new tasks and log the creation of these tasks with a unique identifier.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TaskCounter:
    """
    A class to manage and count tasks.

    This class is responsible for maintaining a counter of tasks and providing a method to create new tasks with unique
    identifiers. It also logs the creation of each new task.
    """

    def __init__(self):
        """
        Initializes the TaskCounter with a logger.
        """
        self.counter = 0
        self._logger = CustomLogger()

    def new_task(self, name: str) -> str:
        """
        Creates a new task with a unique identifier and logs the creation.

        Args:
            name (str): The name of the task.

        Returns:
            str: The new task name with a unique identifier.

        Raises:
            ValueError: If the task name is empty.
        """
        if not name:
            self._logger.error(ValueError("Task name cannot be empty."), self.__class__.__name__)
            raise ValueError("Task name cannot be empty.")

        self.counter += 1
        self._logger.debug(f"TaskCounter.new_task: [NEW] [{self.counter}]{name}")
        return f"[{self.counter}]{name}"
