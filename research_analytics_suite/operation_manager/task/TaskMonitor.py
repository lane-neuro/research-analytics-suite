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
from research_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from research_analytics_suite.operation_manager.operations.persistent.ConsoleOperation import ConsoleOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class TaskMonitor:
    """Monitors and manages tasks."""

    def __init__(self, task_creator, sequencer):
        """
        Initializes the TaskMonitor with the given parameters.

        Args:
            task_creator: The task creator.
            sequencer: The operations sequencer.
        """
        self.task_creator = task_creator
        self.sequencer = sequencer
        self._logger = CustomLogger()

        from research_analytics_suite.operation_manager.OperationControl import OperationControl
        self.op_control = OperationControl()

    async def handle_tasks(self):
        """Handles the execution and monitoring of tasks."""
        self._logger.debug("handle_tasks: [INIT]")
        for task in self.task_creator.tasks.copy():
            self._logger.debug(f"handle_tasks: [CHECK] {task.get_name()}")
            if task.done():
                operation = self.sequencer.find_operation_by_task(task)
                try:
                    self._logger.debug(f"handle_tasks: [OP] {task.get_name()}")
                    if operation is not None:
                        if isinstance(operation, ABCOperation):
                            output = operation.get_result()
                            operation.add_log_entry(f"handle_tasks: [OUTPUT] {output}")

                        self._logger.info(f"handle_tasks: [DONE] {task.get_name()}")
                    else:
                        self._logger.error(Exception(
                            f"handle_tasks: [ERROR] No operations found for task {task.get_name()}"), self)
                except Exception as e:
                    self._logger.error(e, self)
                finally:
                    if operation:
                        self.task_creator.tasks.remove(task)
                        if not operation.persistent:
                            self.sequencer.remove_operation_from_sequencer(operation)

                        if isinstance(operation, ConsoleOperation):
                            self.sequencer.op_.console_operation_in_progress = False
