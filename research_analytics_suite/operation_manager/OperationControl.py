"""
OperationControl Module

This module defines the OperationControl class, which is responsible for managing and executing operations in the
queue. It integrates various components like the operations queue, manager, operation_executor, and checker to manage the
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

from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.operation_manager.OperationExecutor import OperationExecutor
from research_analytics_suite.operation_manager.OperationLifecycleManager import OperationLifecycleManager
from research_analytics_suite.operation_manager.OperationManager import OperationManager
from research_analytics_suite.operation_manager.OperationQueue import OperationQueue
from research_analytics_suite.operation_manager.OperationStatusChecker import OperationStatusChecker
from research_analytics_suite.operation_manager.PersistentOperationChecker import PersistentOperationChecker
from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator
from research_analytics_suite.operation_manager.task.TaskMonitor import TaskMonitor
from research_analytics_suite.utils.CustomLogger import CustomLogger
from research_analytics_suite.utils.UserInputManager import UserInputManager


class OperationControl:
    """A class for handling the lifecycle of Operation instances."""
    SLEEP_TIME = 0.15

    def __init__(self, sleep_time: float = 0.15):
        """
        Initializes the OperationControl with various components.
        """
        self._logger = CustomLogger()
        self.workspace = Workspace()
        self.main_loop = asyncio.get_event_loop()
        self.console_operation_in_progress = False

        self.queue = OperationQueue()
        self.task_creator = TaskCreator(queue=self.queue)
        self.task_monitor = TaskMonitor(task_creator=self.task_creator, queue=self.queue, operation_control=self)

        self.local_vars = locals()

        self.SLEEP_TIME = sleep_time

        self.operation_manager = OperationManager(operation_control=self, queue=self.queue,
                                                  task_creator=self.task_creator)
        self.operation_executor = OperationExecutor(operation_control=self, queue=self.queue,
                                                    task_creator=self.task_creator)
        self.operation_status_checker = OperationStatusChecker(operation_control=self, queue=self.queue)
        self.user_input_manager = UserInputManager(operation_control=self)
        self.persistent_operation_checker = PersistentOperationChecker(operation_control=self,
                                                                       operation_manager=self.operation_manager,
                                                                       queue=self.queue,
                                                                       task_creator=self.task_creator)
        self.lifecycle_manager = OperationLifecycleManager(queue=self.queue, operation_manager=self.operation_manager,
                                                           executor=self.operation_executor,
                                                           task_monitor=self.task_monitor,
                                                           persistent_op_checker=self.persistent_operation_checker)

    async def start(self):
        """Starts the operations handler."""
        self.main_loop.run_forever()

    async def exec_loop(self):
        """Executes the main loop of the operations manager."""
        while True:
            await self.lifecycle_manager.exec_loop()
            await asyncio.sleep(self.SLEEP_TIME)
