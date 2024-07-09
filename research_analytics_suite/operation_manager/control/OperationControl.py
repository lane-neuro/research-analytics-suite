"""
OperationControl Module

This module defines the OperationControl class, which is responsible for managing and executing operations in the
sequencer. It integrates various components like the operations sequencer, manager, operation_executor, and checker to manage the
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

from research_analytics_suite.operation_manager.execution.OperationExecutor import OperationExecutor
from research_analytics_suite.operation_manager.management.OperationLifecycleManager import OperationLifecycleManager
from research_analytics_suite.operation_manager.management.OperationManager import OperationManager
from research_analytics_suite.operation_manager.management.OperationSequencer import OperationSequencer
from research_analytics_suite.operation_manager.management.OperationStatusChecker import OperationStatusChecker
from research_analytics_suite.operation_manager.management.SystemOperationChecker import SystemOperationChecker
from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator
from research_analytics_suite.operation_manager.task.TaskMonitor import TaskMonitor
from research_analytics_suite.utils.CustomLogger import CustomLogger


class OperationControl:
    """A class for handling the lifecycle of Operation instances."""
    SLEEP_TIME = 0.001
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Initializes the OperationControl with various components.
        """
        if not hasattr(self, '_initialized'):
            self._logger = CustomLogger()
            self.workspace = None
            self.console_operation_in_progress = False

            self.sequencer = None
            self.task_creator = None
            self.task_monitor = None

            self.operation_manager = None
            self.operation_executor = None
            self.operation_status_checker = None
            self.user_input_manager = None
            self.system_op_checker = None
            self.lifecycle_manager = None

            self._initialized = False

            try:
                self.main_loop = asyncio.get_event_loop()
            except Exception as e:
                self._logger.error(e, self.__class__.__name__)

    async def initialize(self):
        if not self._initialized:
            async with OperationControl._lock:
                if not self._initialized:
                    self._logger.debug("OperationControl.initialize: Initializing OperationControl.")

                    from research_analytics_suite.data_engine.Workspace import Workspace
                    self.workspace = Workspace()

                    self.main_loop = asyncio.get_event_loop()
                    self.console_operation_in_progress = False

                    self.sequencer = OperationSequencer()
                    self.task_creator = TaskCreator(sequencer=self.sequencer)
                    self.task_monitor = TaskMonitor(task_creator=self.task_creator, sequencer=self.sequencer)

                    self.operation_manager = OperationManager(sequencer=self.sequencer, task_creator=self.task_creator)
                    self.operation_executor = OperationExecutor(sequencer=self.sequencer, task_creator=self.task_creator)
                    self.operation_status_checker = OperationStatusChecker(sequencer=self.sequencer)

                    from research_analytics_suite.commands.UserInputManager import UserInputManager
                    self.user_input_manager = UserInputManager()
                    self.system_op_checker = SystemOperationChecker(sequencer=self.sequencer,
                                                                    task_creator=self.task_creator)
                    self.lifecycle_manager = OperationLifecycleManager(sequencer=self.sequencer,
                                                                       operation_manager=self.operation_manager,
                                                                       executor=self.operation_executor,
                                                                       task_monitor=self.task_monitor,
                                                                       system_op_checker=self.system_op_checker)
                    self._initialized = True
                    self._logger.debug("OperationControl.initialize: OperationControl initialized.")

    async def start(self):
        """Starts the operations handler."""
        self.main_loop.run_forever()

    async def exec_loop(self):
        """Executes the main loop of the operations manager."""
        while True:
            await self.lifecycle_manager.exec_loop()
            await asyncio.sleep(self.SLEEP_TIME)
