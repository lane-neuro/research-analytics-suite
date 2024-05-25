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
import logging
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

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    def __init__(self, sleep_time: float = 0.15):
        """
        Initializes the OperationHandler with an OperationQueue and an ErrorHandler instance.
        """
        nest_asyncio.apply()
        self.setup_logger()
        self.main_loop = asyncio.get_event_loop()
        self.error_handler = ErrorHandler()
        self.queue = OperationQueue()

        self.console_operation_in_progress = False
        self.log_message_queue = asyncio.Queue()
        self.local_vars = locals()

        self.task_manager = TaskManager(self, logger, self.error_handler, self.queue)

        self.sleep_time = sleep_time

    async def start(self):
        """
        Starts the operation handler.
        """
        asyncio.get_event_loop().run_forever()

    def setup_logger(self):
        """
        Sets up the logger with a timestamp.
        """
        # Create a handler
        handler = logging.StreamHandler()

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(handler)

        # Add a log message to the queue whenever a new log is generated
        logger.addFilter(lambda record: self.log_message(record.getMessage()))

    def log_message(self, message):
        """Send a log message to the queue."""
        self.log_message_queue.put_nowait(message)

    async def add_operation(self, func, name: str = "Operation") -> Operation:
        """
        Creates a new Operation and adds it to the queue.

        Args:
            func (callable): The function to be executed by the Operation.
            name (str, optional): The name of the Operation. Defaults to "Operation".
        """
        logger.info(f"add_operation: [START] {name}")
        operation = Operation(name=name, error_handler=self.error_handler, func=func)
        logger.info(f"add_operation: New Operation: {operation.name}")
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
        logger.debug(f"add_custom_operation: New Operation: {operation.name}")
        await self.queue.add_operation_to_queue(operation)

    async def add_operation_if_not_exists(self, operation_type, *args, **kwargs):
        # Check if a task of operation_type is running or in the queue
        if (not any(isinstance(task, operation_type)
                    and task.status in ["running", "started"] for task in self.task_manager.tasks)
                and not any(isinstance(operation_chain.head.operation, operation_type) for operation_chain
                            in self.queue.queue)):
            await self.queue.add_operation_to_queue(operation_type(*args, **kwargs))
            logger.info(f"add_operation_if_not_exists: [QUEUE] {operation_type.__name__} - Added to queue")

    async def start_operations(self) -> None:
        for operation_chain in self.queue.queue:
            if isinstance(operation_chain, OperationChain):
                current_node = operation_chain.head
                while current_node is not None:
                    operation = current_node.operation
                    if operation.status == "idle":
                        await operation.start()
                        operation.status = "started"
                        logger.debug(f"start_operations: [START] {operation.name}")
                    current_node = current_node.next_node
            else:
                operation = operation_chain.operation
                if operation.status == "idle":
                    await operation.start()
                    operation.status = "started"
                    logger.debug(f"start_operations: [START] {operation.name}")

    async def resume_operation(self, operation: Operation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (Operation): The operation to resume.
        """
        if operation.status == "paused":
            await operation.resume()
            operation.status = "running"

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
            operation.status = "paused"

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
        operation.status = "stopped"

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

    async def process_user_input(self, user_input) -> str:
        """
        Processes user input from the console.

        This method takes user input from the console and processes it. It can be extended to include additional
        functionality as needed.

        Args:
            user_input (str): The user input to process.

        Returns:
            str: The response to the user input.
        """

        if user_input == "stop":
            await self.stop_all_operations()
            return "OperationHandler.process_user_input: Stopping all operations..."

        elif user_input == "pause":
            await self.pause_all_operations()
            return "OperationHandler.process_user_input: Pausing all operations..."

        elif user_input == "resume":
            await self.resume_all_operations()
            return "OperationHandler.process_user_input: Resuming all operations..."

        elif user_input == "resources":
            for operation_list in self.queue.queue:
                operation_node = self.queue.get_operation_from_chain(operation_list)
                if isinstance(operation_node, ResourceMonitorOperation):
                    cpu_usage = operation_node.cpu_usage
                    memory_usage = operation_node.memory_usage
                    logger.info(f"OperationHandler.process_user_input: Resource Usage: CPU - {cpu_usage}, "
                                f"MEMORY - {memory_usage}")
            return "OperationHandler.process_user_input: Displaying system resources."

        elif user_input == "tasks":
            for task in self.task_manager.tasks:
                operation = self.queue.get_operation_by_task(task)
                if operation:
                    logger.info(f"OperationHandler.process_user_input: Task: {task.get_name()} - {operation.status}")
            return "OperationHandler.process_user_input: Displaying all tasks..."

        elif user_input == "queue":
            for queue_chain in self.queue.queue:
                operation = queue_chain.head.operation
                logger.info(f"OperationHandler.process_user_input: Operation: {operation.task.get_name()} - "
                            f"{operation.status}")
            return "OperationHandler.process_user_input: Displaying all operations in the queue..."

        elif user_input == "vars":
            logger.info(f"OperationHandler.process_user_input: Local Vars: {self.local_vars}")
            return "OperationHandler.process_user_input: Displaying local vars..."

        else:
            logger.debug(f"OperationHandler.process_user_input: Adding custom operation with func: {user_input}")
            await self.add_custom_operation(user_input, "ConsoleInput")
            return f"OperationHandler.process_user_input: Added custom operation with func: {user_input}"

    async def execute_operation(self, operation) -> asyncio.Task:
        nest_asyncio.apply()
        try:
            if operation.status == "started":
                logger.info(f"execute_operation: [RUN] {operation.task.get_name()}")
                await operation.execute()
                operation.status = "completed"
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
        logger.debug("OperationHandler: Queue Size: " + str(self.queue.size()))

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
                    logger.debug(f"execute_all: [START] {operation.name} - {operation.status} - {operation.task}")

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
            await self.add_operation_if_not_exists(ConsoleOperation, self.error_handler, self, logger,
                                                   self.local_vars, name="ConsoleOperation", prompt="")
            self.console_operation_in_progress = True

        # Check if a ResourceMonitorOperation is already running
        if not any(isinstance(task, ResourceMonitorOperation) for task in self.task_manager.tasks):
            await self.add_operation_if_not_exists(ResourceMonitorOperation, self.error_handler)

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.
        """

        logger.debug("Starting exec_loop")

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
