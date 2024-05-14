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
from neurobehavioral_analytics_suite.operation_handler import BaseOperation
from neurobehavioral_analytics_suite.operation_handler.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.operation_handler.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.operation_handler.ResourceMonitorOperation import ResourceMonitorOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.operation_handler.OperationQueue import OperationQueue

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TaskCounter:
    def __init__(self):
        self.counter = 0

    def new_task(self, name: str) -> str:
        self.counter += 1
        logger.debug(f"TaskCounter.new_task: [NEW] [{self.counter}]{name}")
        return f" [{self.counter}]" + name


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
        self.console_operation_in_progress = False
        self.setup_logger()
        self.local_vars = locals()

        self.task_counter = TaskCounter()
        self.active_tasks = set()
        self.tasks = []

        self.sleep_time = sleep_time

        nest_asyncio.apply()
        self.main_loop = asyncio.get_event_loop()
        self.error_handler = ErrorHandler()
        self.queue = OperationQueue()

        # self.main_loop.create_task(self.exec_loop())

        # Initialize the exec_loop coroutine without creating a task
        self.exec_loop_coroutine = self.exec_loop()

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

    async def start_operations(self) -> None:
        for operation in self.queue.queue:
            if operation.status == "idle":
                await operation.start()
                logger.debug(f"start_operations: [START] {operation.name}")

    async def execute_operation(self, operation: BaseOperation) -> asyncio.Task:
        nest_asyncio.apply()
        try:
            if operation.status == "started" or operation.status == "idle":
                operation.task = asyncio.get_event_loop().create_task(operation.execute(),
                                                                      name=self.task_counter.new_task(operation.name))
                operation.task.type = type(operation)  # Add a 'type' attribute to the task
                logger.info(f"execute_operation: [RUN] {operation.task.get_name()}")

                self.tasks.append(operation.task)
                return operation.task  # Return the coroutine, not the result of the coroutine
        except Exception as e:
            self.error_handler.handle_error(e, self)

    def pause_operation(self, operation: BaseOperation) -> None:
        """
        Pauses a specific operation.

        Args:
            operation (Operation): The operation to pause.
        """
        if operation.status == "running":
            operation.pause()

    def resume_operation(self, operation: BaseOperation) -> None:
        """
        Resumes a specific operation.

        Args:
            operation (Operation): The operation to resume.
        """
        if operation.status == "paused":
            operation.resume()

    def stop_operation(self, operation: BaseOperation) -> None:
        """
        Stops a specific operation.

        Args:
            operation (Operation): The operation to stop.
        """
        if operation.status in ["running", "paused"]:
            operation.stop()

    async def add_custom_operation(self, func, name: str = "CustomOperation"):
        """
        Creates a new CustomOperation and adds it to the queue.

        Args:
            func: The func to be processed by the CustomOperation.
            name: The name of the CustomOperation.
        """

        operation = CustomOperation(self.error_handler, func, self.local_vars, name)
        await self.queue.add_operation(operation)

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
            self.stop_all_operations()
            return "OperationHandler.process_user_input: Stopping all operations..."

        elif user_input == "pause":
            self.pause_all_operations()
            return "OperationHandler.process_user_input: Pausing all operations..."

        elif user_input == "resume":
            self.resume_all_operations()
            return "OperationHandler.process_user_input: Resuming all operations..."

        elif user_input == "resources":
            for operation in self.queue.queue:
                if isinstance(operation, ResourceMonitorOperation):
                    cpu_usage = operation.cpu_usage
                    memory_usage = operation.memory_usage
                    logger.info(f"OperationHandler.process_user_input: Resource Usage: CPU - {cpu_usage}, "
                                f"MEMORY - {memory_usage}")
            return "OperationHandler.process_user_input: No active ResourceMonitorOperation found."

        elif user_input == "tasks":
            for task in self.tasks:
                logger.info(f"OperationHandler.process_user_input: Task:"
                            f"{task.get_name()} - {task.type} - {self.queue.get_operation_by_task(task).status}")
            return "OperationHandler.process_user_input: Displaying all tasks..."

        elif user_input == "queue":
            for operation in self.queue.queue:
                logger.info(f"OperationHandler.process_user_input: Operation: {operation.name} - {operation.status}")
            return "OperationHandler.process_user_input: Displaying all operations in the queue..."

        elif user_input == "vars":
            logger.info(f"OperationHandler.process_user_input: Local Vars: {self.local_vars}")
            return "OperationHandler.process_user_input: Displaying local vars..."

        else:
            logger.debug(f"OperationHandler.process_user_input: Adding custom operation with func: {user_input}")
            self.local_vars = await self.add_custom_operation(user_input, "ConsoleInput")
            return f"OperationHandler.process_user_input: Added custom operation with func: {user_input}"

    def stop_all_operations(self):
        """
        Stops all operations in the queue.
        """

        for operation in self.queue.queue:
            self.stop_operation(operation)

    def pause_all_operations(self):
        """
        Pauses all operations in the queue.
        """

        for operation in self.queue.queue:
            operation.pause()

    def resume_all_operations(self):
        """
        Resumes all paused operations in the queue.
        """

        for operation in self.queue.queue:
            if operation.status == "paused":
                operation.resume()

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

        return {operation: operation.status for operation in self.queue.queue}

    async def start(self):
        """
        Starts the operation handler.
        """
        asyncio.get_event_loop().run_forever()

    async def execute_all(self) -> None:
        """
        Executes all Operation instances in the queue.

        This method uses the Dask client to execute the operations asynchronously. It waits for all operations to
        complete before returning.

        Raises:
            Exception: If an exception occurs during the execution of an operation, it is caught and handled by the
            ErrorHandler instance.
        """

        nest_asyncio.apply()
        # logger.info("OperationHandler: Queue Size: " + str(len(self.queue.queue)))

        self.active_tasks = set()  # Use a set instead of a list

        for operation in self.queue.queue:
            # Ensure operation.task is a Task, not a coroutine
            if asyncio.iscoroutine(operation.task):
                logger.debug(f"execute_all: Creating task for {operation}")
                operation.task = asyncio.create_task(operation.task)

            # Do not execute ConsoleOperation and ResourceMonitorOperation if they are already running or in
            # self.active_tasks
            if operation.task and not operation.task.done() and operation.task not in self.active_tasks:
                logger.debug(f"execute_all: {operation} is already running")
                pass
            else:
                # Add the task for the operation to self.active_tasks
                self.active_tasks.add(asyncio.create_task(self.execute_operation(operation)))

    async def handle_tasks(self) -> None:
        for task in self.tasks.copy():  # Create a copy for iteration
            if task.done():
                try:
                    logger.debug(f"handle_tasks: [START] {task.get_name()}")
                    output = task.result()  # This will re-raise any exceptions that occurred.
                    if task.type == CustomOperation:
                        self.local_vars = output
                    logger.debug(f"handle_tasks: [DONE] {task.get_name()}")
                    logger.info(f"handle_tasks: [OUTPUT] {output}")
                except Exception as e:
                    self.error_handler.handle_error(e, self)
                finally:
                    operation = self.queue.get_operation_by_task(task)
                    if isinstance(operation, ConsoleOperation):
                        self.console_operation_in_progress = False
                    self.tasks.remove(task)
                    await self.queue.remove_operation(operation)

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.
        """

        logger.debug("Starting exec_loop")

        while True:
            try:
                if not self.console_operation_in_progress and \
                        not any(isinstance(task, ConsoleOperation) and not task.done() for task in self.tasks) and \
                        not any(isinstance(operation, ConsoleOperation) for operation in self.queue.queue):
                    await self.queue.add_operation(ConsoleOperation(self.error_handler, self, logger, self.local_vars))
                    logger.info("exec_loop: [QUEUE] Console - Added to queue")
                    self.console_operation_in_progress = True

                if not any(isinstance(task, ResourceMonitorOperation) and not task.done() for task in self.tasks) and \
                        not any(isinstance(operation, ResourceMonitorOperation) for operation in self.queue.queue):
                    await self.queue.add_operation(ResourceMonitorOperation(self.error_handler))
                    logger.info("exec_loop: [QUEUE] ResourceMonitor - Added to queue")

                # Start all operations in the queue
                await self.start_operations()

                # Execute all operations in the queue only if there are no ConsoleOperation or
                # ResourceMonitorOperation tasks running
                if not any(isinstance(task, (ConsoleOperation, ResourceMonitorOperation)) for task in self.tasks):
                    await self.execute_all()

                # Handle tasks
                await self.handle_tasks()

            except Exception as e:
                self.error_handler.handle_error(e, self)
            finally:
                await asyncio.sleep(self.sleep_time)
