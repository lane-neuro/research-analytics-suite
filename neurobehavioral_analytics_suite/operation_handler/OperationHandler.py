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
from concurrent.futures import ProcessPoolExecutor

import nest_asyncio

from neurobehavioral_analytics_suite.operation_handler.OperationChain import OperationChain
from neurobehavioral_analytics_suite.operation_handler.TaskManager import TaskManager
from neurobehavioral_analytics_suite.operation_handler.operations.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_handler.operations.Operation import Operation
from neurobehavioral_analytics_suite.operation_handler.operations.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_handler.operations.ResourceMonitorOperation import \
    ResourceMonitorOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.operation_handler.OperationQueue import OperationQueue
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

    async def start(self):
        """
        Starts the operation handler.
        """
        asyncio.get_event_loop().run_forever()

    async def add_operation(self, func, name: str = "Operation") -> Operation:
        """
        Creates a new Operation and adds it to the queue.

        Args:
            func (callable): The function to be executed by the Operation.
            name (str, optional): The name of the Operation. Defaults to "Operation".
        """
        self.logger.info(f"add_operation: [START] {name}")
        operation = Operation(name=name, error_handler=self.error_handler, func=func)
        self.logger.info(f"add_operation: New Operation: {operation.name}")
        await self.queue.add_operation_to_queue(operation)
        return operation

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

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs):
        # Check if a task of operation_type is running or in the queue
        if (not any(isinstance(task, operation_type)
                    and task.status in ["running", "started"] for task in self.task_manager.tasks)
                and not any(isinstance(operation_chain.head.operation, operation_type) for operation_chain
                            in self.queue.queue)):
            await self.queue.add_operation_to_queue(operation_type(*args, **kwargs))
            self.logger.info(f"add_operation_if_not_exists: [QUEUE] {operation_type.__name__} - Added to queue")

    async def start_operations(self) -> None:
        for operation_chain in self.queue.queue:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    operation = current_node.operation
                    if operation.status == "idle":
                        await operation.init_operation()
                        await operation.start()
                        self.logger.debug(f"start_operations: [START] {operation.name}")
                    current_node = current_node.next_node
            else:
                operation = operation_chain.operation
                if operation.status == "idle":
                    await operation.init_operation()
                    await operation.start()
                    self.logger.debug(f"start_operations: [START] {operation.name}")

    async def resume_operation(self, operation: Operation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (Operation): The operation to resume.
        """
        if operation.status == "paused":
            await operation.resume()

    async def resume_all_operations(self):
        """
        Resumes all paused operations in the queue.
        """

        for operation_list in self.queue.queue:
            operation = self.queue.get_operation_from_chain(operation_list)
            if operation.status == "paused":
                await operation.resume()

    async def pause_operation(self, operation: Operation) -> None:
        """
        Pauses a specific operation.

        Args:
            operation (Operation): The operation to pause.
        """
        if operation.status == "running":
            await operation.pause()

    async def pause_all_operations(self):
        """
        Pauses all operations in the queue.
        """

        for operation_list in self.queue.queue:
            operation = self.queue.get_operation_from_chain(operation_list)
            await self.pause_operation(operation)

    async def stop_operation(self, operation: Operation) -> None:
        """
        Stops a specific operation.

        Args:
            operation (Operation): The operation to stop.
        """
        await operation.stop()

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

    def get_operation_status(self, operation) -> str:
        """
        Returns the status of a specific operation.

        Args:
            operation (Operation): The operation to get the status of.

        Returns:
            str: The status of the operation.
        """
        return operation.status

    def get_all_operations_status(self):
        """
        Returns the status of all operations in the queue.

        Returns:
            dict: A dictionary mapping operation instances to their status.
        """
        status_dict = {}
        for operation_node in self.queue.queue:
            if isinstance(operation_node, OperationChain):
                current_node = operation_node.head
                while current_node is not None:
                    status_dict[current_node.operation] = current_node.operation.status
                    current_node = current_node.next_node
            else:
                status_dict[operation_node] = operation_node.status
        return status_dict

    async def execute_operation(self, operation) -> asyncio.Task:
        nest_asyncio.apply()
        try:
            if operation.status == "started":
                self.logger.info(f"execute_operation: [RUN] {operation.task.get_name()}")
                await operation.execute()
                return operation.task
        except Exception as e:
            self.error_handler.handle_error(e, self)

    async def execute_all(self) -> None:
        """
        Executes all Operation instances in the queue.

        This method executes the operations asynchronously. It waits for all operations tocomplete before returning.

        Raises:
            Exception: If an exception occurs during the execution of an operation, it is caught and handled by the
            ErrorHandler instance.
        """

        nest_asyncio.apply()
        self.logger.debug("OperationHandler: Queue Size: " + str(self.queue.size()))

        # Create a copy of the queue for iteration
        queue_copy = set(self.queue.queue)

        for operation_chain in queue_copy:
            top_operations = set()
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                if current_node is not None:
                    top_operations.add(current_node.operation)
            else:
                top_operations.add(operation_chain.operation)

            for operation in top_operations:
                if not operation.task or operation.task.done():
                    if isinstance(operation, ConsoleOperation) and not self.console_operation_in_progress:
                        continue
                    self.logger.debug(f"execute_all: [START] {operation.name} - {operation.status} - {operation.task}")

                    if not operation.task:
                        operation.task = self.task_manager.create_task(self.execute_operation(operation),
                                                                       name=operation.name)
                    if isinstance(operation, ConsoleOperation):
                        self.console_operation_in_progress = True

    async def check_persistent_operations(self):
        """
        Checks for persistent operations and adds them to the queue if they are not already present.
        """

        if not self.console_operation_in_progress:
            await self.add_operation_if_not_exists(ConsoleOperation, self.error_handler, self.user_input_handler,
                                                   self.logger,
                                                   self.local_vars, name="ConsoleOperation", prompt="")
            self.console_operation_in_progress = True

        # Check if a ResourceMonitorOperation is already running
        if not any(isinstance(task, ResourceMonitorOperation) for task in self.task_manager.tasks):
            await self.add_operation_if_not_exists(ResourceMonitorOperation, self.error_handler)

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
