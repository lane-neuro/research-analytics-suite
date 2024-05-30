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
from neurobehavioral_analytics_suite.operation_manager.operation.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class UserInputManager:
    def __init__(self, operation_handler, logger, error_handler: ErrorHandler):
        self.operation_handler = operation_handler
        self.logger = logger
        self.error_handler = error_handler

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
            await self.operation_handler.stop_all_operations()
            return "UserInputHandler.process_user_input: Stopping all operations..."

        elif user_input == "pause":
            await self.operation_handler.pause_all_operations()
            return "UserInputHandler.process_user_input: Pausing all operations..."

        elif user_input == "resume":
            await self.operation_handler.resume_all_operations()
            return "UserInputHandler.process_user_input: Resuming all operations..."

        elif user_input == "resources":
            for operation_list in self.operation_handler.queue.queue:
                operation_node = self.operation_handler.queue.get_operation_from_chain(operation_list)
                if isinstance(operation_node, ResourceMonitorOperation):
                    cpu_usage = operation_node.cpu_usage
                    memory_usage = operation_node.memory_usage
                    self.logger.info(f"UserInputHandler.process_user_input: Resource Usage: CPU - {cpu_usage}, "
                                     f"MEMORY - {memory_usage}")
            return "UserInputHandler.process_user_input: Displaying system resources."

        elif user_input == "tasks":
            for task in self.operation_handler.task_manager.tasks:
                operation = self.operation_handler.queue.get_operation_by_task(task)
                if operation:
                    self.logger.info(f"UserInputHandler.process_user_input: Task: {task.get_name()} - "
                                     f"{operation.status}")
            return "UserInputHandler.process_user_input: Displaying all tasks..."

        elif user_input == "queue":
            for queue_chain in self.operation_handler.queue.queue:
                operation = queue_chain.head.operation
                self.logger.info(f"UserInputHandler.process_user_input: Operation: {operation.task.get_name()} - "
                                 f"{operation.status}")
            return "UserInputHandler.process_user_input: Displaying all operations in the queue..."

        elif user_input == "vars":
            self.logger.info(f"UserInputHandler.process_user_input: Local Vars: {self.operation_handler.local_vars}")
            return "UserInputHandler.process_user_input: Displaying local vars..."

        else:
            self.logger.debug(f"UserInputHandler.process_user_input: Adding custom operation with func: {user_input}")
            await self.operation_handler.add_custom_operation(user_input, "ConsoleInput")
            return f"UserInputHandler.process_user_input: Added custom operation with func: {user_input}"
