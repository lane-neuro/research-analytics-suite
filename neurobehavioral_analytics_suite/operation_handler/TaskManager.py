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
import asyncio

from neurobehavioral_analytics_suite.operation_handler.TaskCounter import TaskCounter
from neurobehavioral_analytics_suite.operation_handler.operations.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_handler.operations.CustomOperation import CustomOperation


class TaskManager:
    def __init__(self, operation_handler, logger, error_handler, queue):
        self.task_counter = TaskCounter(logger)
        self.operation_handler = operation_handler
        self.tasks = set()
        self.error_handler = error_handler
        self.logger = logger
        self.queue = queue

    def create_task(self, coro, name):
        """
        Private method to create tasks. This method should be used instead of asyncio.create_task
        within the OperationHandler class.
        """
        task = asyncio.create_task(coro, name=self.task_counter.new_task(name))
        self.tasks.add(task)
        return task

    async def handle_tasks(self) -> None:
        self.logger.debug("handle_tasks: [INIT]")
        for task in self.tasks.copy():
            self.logger.debug(f"handle_tasks: [CHECK] {task.get_name()}")
            if task.done():
                operation = self.queue.get_operation_by_task(task)
                try:
                    self.logger.debug(f"handle_tasks: [START] {task.get_name()}")
                    if operation is not None:
                        await operation.task
                        if isinstance(operation, CustomOperation):
                            output = operation.result_output
                            self.operation_handler.local_vars = output
                            self.logger.debug(f"handle_tasks: [OUTPUT] {output}")
                        self.logger.debug(f"handle_tasks: [DONE] {task.get_name()}")
                    else:
                        self.logger.debug(f"handle_tasks: [ERROR] No operation found for task {task.get_name()}")
                except Exception as e:
                    self.error_handler.handle_error(e, self)
                finally:
                    if operation:
                        self.tasks.remove(task)
                        if not operation.persistent:
                            self.queue.remove_operation_from_queue(operation)

                        if isinstance(operation, ConsoleOperation):
                            self.operation_handler.console_operation_in_progress = False
