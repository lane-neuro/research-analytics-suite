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
logger.setLevel(logging.DEBUG)


class TaskCounter:
    def __init__(self):
        self.counter = 0

    def new_task(self, name: str) -> str:
        self.counter += 1
        logger.info(f"TaskCounter.new_task: [NEW] [{self.counter}]{name}")
        return f" [{self.counter}]" + name


class OperationHandler:
    """
    A class for handling the lifecycle of Operation instances.

    This class provides methods for starting, executing, pausing, stopping, and resuming operations. It uses an
    instance of OperationQueue to manage the queue of operations.

    Attributes:
        queue (OperationQueue): A queue for storing Operation instances.
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        console (ConsoleOperation): An instance of ConsoleOperation for handling user input from the console.
        monitor (resource_monitor): A function for monitoring system resources.
        main_loop (asyncio.AbstractEventLoop): The main asyncio event loop.
    """

    def __init__(self, sleep_time: float = 0.75):
        """
        Initializes the OperationHandler with an OperationQueue and an ErrorHandler instance.
        """
        self.setup_logger()

        self.task_counter = TaskCounter()
        self.tasks = []

        self.sleep_time = sleep_time

        nest_asyncio.apply()
        self.main_loop = asyncio.get_event_loop()
        self.error_handler = ErrorHandler()
        self.queue = OperationQueue()

        self.console = ConsoleOperation(self.error_handler, self, self.main_loop, logger,
                                        name="ConsoleOperation")
        self.monitor = ResourceMonitorOperation(self.error_handler)

        self.main_loop.create_task(self.exec_loop())

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
                logger.info(f"start_operations: [START] {operation}")

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

    def add_custom_operation(self, data, name: str = "CustomOperation"):
        """
        Creates a new CustomOperation and adds it to the queue.

        Args:
            data: The data to be processed by the CustomOperation.
            name: The name of the CustomOperation.
        """

        operation = CustomOperation(data, self.error_handler, name)
        self.queue.add_operation(operation)

    def process_user_input(self, user_input) -> str:
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
        else:
            logger.info(f"OperationHandler.process_user_input: Adding custom operation with data: {user_input}")
            self.add_custom_operation(user_input, "ConsoleInput")
            return f"OperationHandler.process_user_input: Added custom operation with data: {user_input}"

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
        logger.info("OperationHandler: Queue Size: " + str(len(self.queue.queue)))

        # # Add ConsoleOperation and ResourceMonitorOperation to the queue if they are not already in it
        # if not any(isinstance(operation, ConsoleOperation) for operation in self.queue.queue):
        #     self.queue.add_console_operation(self.console)
        # if not any(isinstance(operation, ResourceMonitorOperation) for operation in self.queue.queue):
        #     self.queue.add_operation(self.monitor)

        for operation in self.queue.queue:
            # Ensure operation.task is a Task, not a coroutine
            if (asyncio.iscoroutine(operation.task)
                    and not isinstance(operation, (ConsoleOperation, ResourceMonitorOperation))):
                operation.task = asyncio.create_task(operation.task, name=self.task_counter.new_task(operation.name))

            # Do not execute ConsoleOperation and ResourceMonitorOperation if they are already running or in self.tasks
            if (operation.task and not operation.task.done()
                    and not isinstance(operation, (ConsoleOperation, ResourceMonitorOperation))
                    and not any(task._coro == operation.task for task in self.tasks)):
                print(f"execute_all: {operation} is already running")
                pass
            else:
                # Check if a task for the operation already exists in self.tasks
                if not any(task._coro == operation.task for task in self.tasks):
                    self.tasks.append(asyncio.create_task(self.execute_operation(operation),
                                                          name=self.task_counter.new_task(operation.name)))

    async def handle_tasks(self) -> None:
        for task in self.tasks.copy():  # Create a copy for iteration
            if task.done():
                try:
                    task.result()  # This will re-raise any exceptions that occurred.
                except Exception as e:
                    self.error_handler.handle_error(e, self)
                finally:
                    logger.info(f"handle_tasks: [DONE] {task.get_name()}")
                    operation = self.queue.get_operation_by_task(task)
                    self.queue.remove_operation(operation)
                    self.tasks.remove(task)  # Safe to modify self.tasks because we're not iterating over it
            else:
                # logger.info(f"handle_tasks: [INCOMPLETE] {task.get_name()}")
                pass

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.
        """

        logger.info("Starting exec_loop")

        while True:
            try:
                # Check if there are any ConsoleOperation tasks running or in the queue
                if not any(isinstance(task, ConsoleOperation) for task in self.tasks) and \
                        not any(isinstance(operation, ConsoleOperation) for operation in self.queue.queue):
                    # If not, add a new ConsoleOperation task to the queue
                    self.queue.add_operation(ConsoleOperation(self.error_handler, self, self.main_loop, logger))

                # Check if there are any ResourceMonitorOperation tasks running or in the queue
                if not any(isinstance(task, ResourceMonitorOperation) for task in self.tasks) and \
                        not any(isinstance(operation, ResourceMonitorOperation) for operation in self.queue.queue):
                    # If not, add a new ResourceMonitorOperation task to the queue
                    self.queue.add_operation(ResourceMonitorOperation(self.error_handler))

                # Execute all operations in the queue
                await self.execute_all()

            except Exception as e:
                self.error_handler.handle_error(e, self)

            await asyncio.sleep(self.sleep_time)