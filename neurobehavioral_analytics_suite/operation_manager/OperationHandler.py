"""
A module that defines the OperationHandler class, which is responsible for managing and executing operations in the
queue. It also handles user input from the console and monitors system resources.

The OperationHandler class provides methods for adding operations to the queue, stopping, pausing, and resuming
operations, and getting the status of operations. It also sets up the asyncio event loop and continuously monitors
for tasks.

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
import nest_asyncio
from neurobehavioral_analytics_suite.operation_manager.OperationChain import OperationChain
from neurobehavioral_analytics_suite.operation_manager.OperationExecutor import OperationExecutor
from neurobehavioral_analytics_suite.operation_manager.OperationManager import OperationManager
from neurobehavioral_analytics_suite.operation_manager.OperationStatusChecker import OperationStatusChecker
from neurobehavioral_analytics_suite.operation_manager.PersistentOperationChecker import PersistentOperationChecker
from neurobehavioral_analytics_suite.operation_manager.TaskManager import TaskManager
from neurobehavioral_analytics_suite.operation_manager.operations.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_manager.operations.Operation import Operation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.operation_manager.OperationQueue import OperationQueue
from neurobehavioral_analytics_suite.utils.UserInputManager import UserInputManager


class OperationHandler:
    """
    A class for handling the lifecycle of Operation instances.

    This class provides methods for starting, executing, pausing, stopping, and resuming operations. It uses an
    instance of OperationQueue to manage the queue of operations.

    Attributes:
        queue (OperationQueue): A queue for storing Operation instances.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        main_loop (asyncio.AbstractEventLoop): The main asyncio event loop.
    """

    def __init__(self, logger, sleep_time: float = 0.15):
        """
        Initializes the OperationHandler with an OperationQueue and an ErrorHandler instance.
        """
        nest_asyncio.apply()
        self.logger = logger
        self.error_handler = ErrorHandler()
        self.main_loop = asyncio.get_event_loop()

        self.queue = OperationQueue(self.logger, self.error_handler)
        self.task_manager = TaskManager(self, self.logger, self.error_handler, self.queue)
        self.user_input_handler = UserInputManager(self, self.logger, self.error_handler)

        self.console_operation_in_progress = False
        self.local_vars = locals()

        self.sleep_time = sleep_time

        self.operation_manager = OperationManager(self.queue, self.logger, self.error_handler)
        self.operation_executor = OperationExecutor(self, self.queue, self.task_manager, self.logger,
                                                    self.error_handler)
        self.operation_status_checker = OperationStatusChecker(self, self.queue)
        self.persistent_operation_checker = PersistentOperationChecker(self, self.queue, self.task_manager, self.logger,
                                                                       self.error_handler)

    async def start(self):
        """
        Starts the operation handler.
        """
        self.main_loop.run_forever()

    async def add_custom_operation(self, func, name: str = "CustomOperation"):
        """
        Creates a new CustomOperation and adds it to the queue.

        Args:
            func: The func to be processed by the CustomOperation.
            name: The name of the CustomOperation.
        """
        operation = CustomOperation(self.error_handler, func, self.local_vars, name)
        self.logger.debug(f"add_custom_operation: New Operation: {operation.name}")
        await self.queue.add_operation_to_queue(operation)

    def task_exists(self, operation_type):
        return (any(isinstance(task, operation_type)
                    and task.status in ["running", "started"] for task in self.task_manager.tasks)
                or any(isinstance(operation_chain.head.operation, operation_type) for operation_chain
                       in self.queue.queue))

    async def add_task(self, operation_type, *args, **kwargs):
        await self.queue.add_operation_to_queue(operation_type(*args, **kwargs))
        self.logger.info(f"add_task: [QUEUE] {operation_type.__name__} - Added to queue")

    async def add_operation(self, func, name: str = "Operation") -> Operation:
        return await self.operation_manager.add_operation(func, name)

    async def pause_operation(self, operation: Operation) -> None:
        await self.operation_manager.pause_operation(operation)

    async def resume_operation(self, operation: Operation) -> None:
        await self.operation_manager.resume_operation(operation)

    async def stop_operation(self, operation: Operation) -> None:
        await self.operation_manager.stop_operation(operation)

    async def execute_operation(self, operation) -> asyncio.Task:
        return await self.operation_executor.execute_operation(operation)

    async def execute_all(self) -> None:
        await self.operation_executor.execute_all()

    def get_operation_status(self, operation) -> str:
        return self.operation_status_checker.get_operation_status(operation)

    def get_all_operations_status(self):
        return self.operation_status_checker.get_all_operations_status()

    async def check_persistent_operations(self):
        await self.persistent_operation_checker.check_persistent_operations()

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs):
        if not self.task_exists(operation_type):
            await self.add_task(operation_type, *args, **kwargs)

    async def start_operations(self) -> None:
        for operation_chain in self.queue.queue:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    operation = current_node.operation
                    if operation.status == "idle":
                        operation.init_operation()
                        await operation.start()
                        self.logger.debug(f"start_operations: [START] {operation.name}")
                    current_node = current_node.next_node
            else:
                operation = operation_chain.operation
                if operation.status == "idle":
                    operation.init_operation()
                    await operation.start()
                    self.logger.debug(f"start_operations: [START] {operation.name}")

    async def resume_all_operations(self):
        """
        Resumes all paused operations in the queue.
        """
        for operation_list in self.queue.queue:
            operation = self.queue.get_operation_from_chain(operation_list)
            await self.resume_operation(operation)

    async def pause_all_operations(self):
        """
        Pauses all operations in the queue.
        """

        for operation_list in self.queue.queue:
            operation = self.queue.get_operation_from_chain(operation_list)
            await self.pause_operation(operation)

    async def stop_all_operations(self):
        """
        Stops all operations in the queue.
        """
        for operation_node in self.queue.queue:
            if isinstance(operation_node, OperationChain):
                current_node = operation_node.head
                while current_node is not None:
                    await self.stop_operation(current_node.operation)
                    current_node = current_node.next_node
            else:
                await self.stop_operation(operation_node)

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.
        """

        self.logger.debug("Starting exec_loop")

        while True:
            try:
                # Check for persistent operations
                await self.check_persistent_operations()

                # Start all operations in the queue
                await self.start_operations()

                # Execute all operations in the queue
                await self.execute_all()

                # Handle any completed tasks
                await self.task_manager.handle_tasks()

            except Exception as e:
                self.error_handler.handle_error(e, self)
            finally:
                await asyncio.sleep(self.sleep_time)