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

from neurobehavioral_analytics_suite.operation_handler.CustomOperation import CustomOperation
from neurobehavioral_analytics_suite.operation_handler.Operation import Operation
from neurobehavioral_analytics_suite.operation_handler.ConsoleOperation import ConsoleOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
from neurobehavioral_analytics_suite.utils.resource_monitor import resource_monitor
from neurobehavioral_analytics_suite.operation_handler.OperationQueue import OperationQueue


class OperationHandler:
    """
    A class for managing and executing operations in the queue.

    This class provides methods for adding operations to the queue, stopping, pausing, and resuming operations, and
    getting the status of operations. It also sets up the asyncio event loop and continuously monitors for tasks.

    Attributes:
        error_handler (ErrorHandler): An instance of ErrorHandler to handle any exceptions that occur.
        queue (OperationQueue): A queue for storing Operation instances.
        console (ConsoleOperation): An instance of ConsoleOperation for handling user input from the console.
        monitor (resource_monitor): A function for monitoring system resources.
        main_loop (asyncio.AbstractEventLoop): The main asyncio event loop.
    """

    def __init__(self):
        """
        Initializes the OperationHandler with an OperationQueue, a ConsoleOperation, and a resource monitor.
        It also sets up the asyncio event loop.
        """

        self.error_handler = ErrorHandler()
        self.queue = OperationQueue()
        self.console = ConsoleOperation(ErrorHandler())
        self.monitor = resource_monitor(ErrorHandler())

        nest_asyncio.apply()
        self.main_loop = asyncio.get_event_loop()
        self.queue.add_persistent_task(self.add_operation_from_input())
        self.queue.add_persistent_task(self.monitor)
        asyncio.ensure_future(self.exec_loop())

    def add_custom_operation(self, data):
        """
        Creates a new CustomOperation and adds it to the queue.

        Args:
            data: The data to be processed by the CustomOperation.
        """

        operation = CustomOperation(data, self.error_handler)
        self.queue.add_operation(operation)

    async def add_operation_from_input(self):
        """
        Continuously gets user input from the console, creates a new CustomOperation based on the input, and adds it
        to the queue.
        """

        while True:
            input_line = await self.console.execute()
            operation = CustomOperation(input_line, self.error_handler)
            self.queue.add_operation(operation)

    def stop_all_operations(self):
        """
        Stops all operations in the queue.
        """

        for operation in self.queue.queue:
            operation.stop()

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

    def get_operation_status(self, operation):
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

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.

        This method sets up the asyncio event loop and continuously monitors for tasks. It waits for user input from
        the console and executes the input as a command. If an exception occurs during the execution of the command,
        it is caught and printed to the console. This method runs indefinitely until the program is stopped.
        """

        while True:
            if not self.queue.is_empty():
                operation = self.queue.get_operation(0)
                task = operation.start()
                try:
                    done, pending = await asyncio.wait([task], return_when=asyncio.FIRST_COMPLETED)
                    for task in list(done):
                        try:
                            result = task.result()
                            print(f"Task completed with result: {result}")
                        except Exception as e:
                            self.error_handler.handle_error(e, task)
                            done.remove(task)
                    self.queue.remove_operation(operation)
                except Exception as e:
                    self.error_handler.handle_error(e, task)
            else:
                await asyncio.sleep(.5)
