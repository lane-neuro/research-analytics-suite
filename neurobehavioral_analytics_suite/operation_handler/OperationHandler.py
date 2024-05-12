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
from neurobehavioral_analytics_suite.operation_handler.ResourceMonitorOperation import ResourceMonitorOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler
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
        self.console = None
        self.monitor = ResourceMonitorOperation(self.error_handler)

        nest_asyncio.apply()
        self.main_loop = asyncio.get_event_loop()
        self.main_loop.create_task(self.exec_loop())
        self.queue.add_persistent_task(self.monitor)

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
        input_line = await self.console.execute()
        operation = CustomOperation(input_line, self.error_handler)
        self.add_custom_operation(operation)

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
            return "Stopping all operations..."
        elif user_input == "pause":
            self.pause_all_operations()
            return "Pausing all operations..."
        elif user_input == "resume":
            self.resume_all_operations()
            return "Resuming all operations..."
        else:
            print(f"Adding custom operation with data: {user_input}")
            self.add_custom_operation(user_input)
            return f"Added custom operation with data: {user_input}"

    def stop_all_operations(self):
        """
        Stops all operations in the queue.
        """

        for operation in self.queue.queue:
            self.stop_operation(operation)

    def stop_operation(self, operation):
        """
        Stops a specific operation.

        Args:
            operation (Operation): The operation to stop.
        """

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

    def start(self):
        """
        Starts the operation handler.
        """

        asyncio.get_event_loop().run_forever()

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.
        """

        print("Starting exec_loop")  # Add logging

        while True:
            #print("In exec_loop")  # Add logging

            if self.queue.console is None or not isinstance(self.queue.console,
                                                            ConsoleOperation) or self.queue.console.complete:
                print("Starting ConsoleOperation")  # Add logging
                self.queue.add_console_operation(self.main_loop)

            if not self.queue.is_empty():
                print("Executing all operations")  # Add logging
                await self.queue.execute_all()

            await asyncio.sleep(.25)
