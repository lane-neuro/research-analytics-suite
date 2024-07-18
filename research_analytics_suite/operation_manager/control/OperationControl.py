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

from research_analytics_suite.commands import link_class_commands, CommandRegistry
from research_analytics_suite.operation_manager.execution.OperationExecutor import OperationExecutor
from research_analytics_suite.operation_manager.management.OperationLifecycleManager import OperationLifecycleManager
from research_analytics_suite.operation_manager.management.OperationManager import OperationManager
from research_analytics_suite.operation_manager.management.OperationSequencer import OperationSequencer
from research_analytics_suite.operation_manager.task.TaskCreator import TaskCreator
from research_analytics_suite.operation_manager.task.TaskMonitor import TaskMonitor
from research_analytics_suite.utils.CustomLogger import CustomLogger


@link_class_commands
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
            self._command_registry = None
            self.workspace = None
            self.console_operation_in_progress = False

            self.sequencer = None
            self.task_creator = None
            self.task_monitor = None

            self.operation_manager = None
            self.operation_executor = None
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
                    self._command_registry = CommandRegistry()
                    self._logger.debug("OperationControl.initialize: Initializing OperationControl.")

                    from research_analytics_suite.data_engine.Workspace import Workspace
                    self.workspace = Workspace()

                    self.main_loop = asyncio.get_event_loop()

                    self.sequencer = OperationSequencer()

                    self.task_creator = TaskCreator(sequencer=self.sequencer)
                    self.task_monitor = TaskMonitor(task_creator=self.task_creator, sequencer=self.sequencer)

                    self.operation_manager = OperationManager(sequencer=self.sequencer, task_creator=self.task_creator)
                    await self.operation_manager.initialize()

                    self.operation_executor = OperationExecutor(sequencer=self.sequencer,
                                                                task_creator=self.task_creator)
                    self.lifecycle_manager = OperationLifecycleManager(sequencer=self.sequencer,
                                                                       operation_manager=self.operation_manager,
                                                                       executor=self.operation_executor,
                                                                       task_monitor=self.task_monitor)

                    self._initialized = True
                    self._logger.debug("OperationControl.initialize: OperationControl initialized.")

    async def start(self):
        """Starts the operations handler."""
        self.main_loop.run_forever()

    async def exec_loop(self):
        """Executes the main loop of the operations manager."""
        while not self.main_loop.is_closed():
            await self.lifecycle_manager.exec_loop()
            await asyncio.sleep(self.SLEEP_TIME)

    async def stop_exec_loop(self):
        """Stops the execution loop."""
        self.operation_manager.resource_monitor.is_loop = False
        self.operation_manager.console_monitor.is_loop = False

        for task in self.task_creator.tasks:
            _op = self.sequencer.find_operation_by_task(task)
            _op.is_loop = False

        self.main_loop.stop()
        self._logger.info("OperationControl: Main loop stopped.")
