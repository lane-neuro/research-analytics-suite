"""
Module description.

Longer description.

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

from neurobehavioral_analytics_suite.utils.Console_UI import Console_UI
from neurobehavioral_analytics_suite.utils.resource_monitor import resource_monitor
from operation_handler.OperationQueue import OperationQueue


class OperationHandler:
    """
    
    """

    def __init__(self):
        """
        
        """

        self.queue = OperationQueue()
        self.console = Console_UI()
        self.monitor = resource_monitor()

        # Apply the nest_asyncio patch to enable nested use of asyncio's event loop
        nest_asyncio.apply()

        # Get the main event loop
        self.main_loop = asyncio.get_event_loop()

        self.persistent_tasks = [
            self.main_loop.create_task(self.console.exec()),
            self.main_loop.create_task(self.monitor),
        ]

        # initialize asyncio primary event loop
        asyncio.ensure_future(self.exec_loop())
        asyncio.get_event_loop().run_forever()

    async def exec_loop(self):
        """
        Executes the main loop of the operation manager.

        This method is responsible for setting up the asyncio event loop and continuously monitoring for tasks.
        It specifically waits for user input from the console and executes the input as a command.
        If an exception occurs during the execution of the command, it is caught and printed to the console.

        Note: This method runs indefinitely until the program is stopped.
        """

        # Start an indefinite loop to monitor asyncio tasks
        while True:
            tasks = self.queue.queue

            # Wait for the tasks to complete
            done, pending = await asyncio.wait(self.persistent_tasks + tasks, return_when=asyncio.FIRST_COMPLETED)

            # Handle the results of the completed tasks
            for task in list(done):
                try:
                    result = task.result()
                    print(f"Task completed with result: {result}")
                except Exception as e:
                    print(f"An error occurred in the task: {e}")
                    done.remove(task)

            # Reschedule the pending tasks
            self.tasks = list(pending)
