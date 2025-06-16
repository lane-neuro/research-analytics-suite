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
from research_analytics_suite.operation_manager.management import OperationSequencer
from research_analytics_suite.operation_manager.operations.core.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.task import TaskCreator
from research_analytics_suite.utils.CustomLogger import CustomLogger
import asyncio


class TaskMonitor:
    """Monitors and manages tasks."""

    def __init__(self, task_creator: TaskCreator, sequencer: OperationSequencer):
        """
        Initializes the TaskMonitor with the given parameters.

        Args:
            task_creator: The task creator.
            sequencer: The operations sequencer.
        """
        self.task_creator = task_creator
        self.sequencer = sequencer
        self._logger = CustomLogger()
        self.paused_tasks = {}

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self.op_control = OperationControl()

    async def handle_tasks(self):
        """Handles the execution and monitoring of tasks."""
        for task in self.task_creator.tasks.copy():
            if task.done():
                operation = self.sequencer.find_operation_by_task(task)
                try:
                    # self._logger.debug(f"handle_tasks: [OP] {task.get_name()}")
                    if operation is not None:
                        if isinstance(operation, BaseOperation) and operation.is_complete:
                            output = await operation.get_results()
                            operation.add_log_entry(f"handle_tasks: [OUTPUT] {output}")
                            self._logger.debug(f"handle_tasks: [DONE] {task.get_name()}")
                    # else:
                    #     self._logger.error(Exception(
                    #         f"handle_tasks: [ERROR] No operations found for task {task.get_name()}"),
                    #         self.__class__.__name__)
                except Exception as e:
                    self._logger.error(e, self.__class__.__name__)
                finally:
                    if operation.is_complete and not operation.is_loop:
                        operation.status = "idle"

    def get_task_statuses(self):
        """Retrieves the status of all tasks."""
        statuses = {}
        for task in self.task_creator.tasks:
            statuses[task.get_name()] = "done" if task.done() else "running"
        return statuses

    def pause_all_tasks(self):
        """Pauses all running tasks."""
        for task in self.task_creator.tasks:
            if not task.done():
                coro = task.get_coro()
                self.paused_tasks[task.get_name()] = coro
                task.cancel()
                self._logger.debug(f"pause_all_tasks: [PAUSE] {task.get_name()}")

    def resume_all_tasks(self):
        """Resumes all paused tasks."""
        for task_name, coro in self.paused_tasks.items():
            new_task = asyncio.create_task(coro, name=task_name)
            self.task_creator.tasks.add(new_task)
            self._logger.debug(f"resume_all_tasks: [RESUME] {task_name}")
        self.paused_tasks.clear()
