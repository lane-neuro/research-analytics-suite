"""
OperationControl Module.

This module defines the OperationControl class, which is responsible for managing and executing operations in the
queue. It integrates various components like the operation queue, manager, operation_executor, and checker to manage the
lifecycle of operations.

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
from neurobehavioral_analytics_suite.operation_manager.OperationExecutor import OperationExecutor
from neurobehavioral_analytics_suite.operation_manager.OperationManager import OperationManager
from neurobehavioral_analytics_suite.operation_manager.OperationStatusChecker import OperationStatusChecker
from neurobehavioral_analytics_suite.operation_manager.PersistentOperationChecker import PersistentOperationChecker
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.operation_manager.OperationQueue import OperationQueue
from neurobehavioral_analytics_suite.utils.UserInputManager import UserInputManager
from neurobehavioral_analytics_suite.operation_manager.OperationLifecycleManager import OperationLifecycleManager
from neurobehavioral_analytics_suite.operation_manager.TaskCreator import TaskCreator
from neurobehavioral_analytics_suite.operation_manager.TaskMonitor import TaskMonitor


class OperationControl:
    """A class for handling the lifecycle of Operation instances."""

    def __init__(self, logger, sleep_time: float = 0.15):
        """
        Initializes the OperationControl with various components.
        """
        self.logger = logger
        self.error_handler = ErrorHandler()
        self.main_loop = asyncio.get_event_loop()

        self.queue = OperationQueue(logger=self.logger, error_handler=self.error_handler)
        self.task_creator = TaskCreator(logger=self.logger, queue=self.queue)
        self.task_monitor = TaskMonitor(task_creator=self.task_creator, queue=self.queue, logger=self.logger,
                                        error_handler=self.error_handler)

        self.console_operation_in_progress = False
        self.local_vars = locals()

        self.sleep_time = sleep_time

        self.operation_manager = OperationManager(operation_control=self, queue=self.queue,
                                                  task_creator=self.task_creator, logger=self.logger,
                                                  error_handler=self.error_handler)
        self.operation_executor = OperationExecutor(operation_control=self, queue=self.queue,
                                                    task_creator=self.task_creator, logger=self.logger,
                                                    error_handler=self.error_handler)
        self.operation_status_checker = OperationStatusChecker(operation_control=self, queue=self.queue)
        self.persistent_operation_checker = PersistentOperationChecker(operation_control=self,
                                                                       operation_manager=self.operation_manager,
                                                                       queue=self.queue,
                                                                       task_creator=self.task_creator,
                                                                       logger=self.logger,
                                                                       error_handler=self.error_handler)
        self.user_input_handler = UserInputManager(operation_control=self, logger=self.logger,
                                                   error_handler=self.error_handler)
        self.lifecycle_manager = OperationLifecycleManager(queue=self.queue, operation_manager=self.operation_manager,
                                                           executor=self.operation_executor,
                                                           task_monitor=self.task_monitor, logger=self.logger,
                                                           persistent_op_checker=self.persistent_operation_checker,
                                                           error_handler=self.error_handler)

    async def start(self):
        """Starts the operation handler."""
        self.main_loop.run_forever()

    async def exec_loop(self):
        """Executes the main loop of the operation manager."""
        await self.lifecycle_manager.exec_loop()
