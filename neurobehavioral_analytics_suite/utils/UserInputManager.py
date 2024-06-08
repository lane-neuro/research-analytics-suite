"""
UserInputManager Module.

This module defines the UserInputManager class, which processes user input from the console within the neurobehavioral
analytics suite. It handles various commands such as stopping, pausing, and resuming operations, as well as displaying
system resources, tasks, and queue status.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""
import dask.distributed

from neurobehavioral_analytics_suite.operation_manager.operations.ABCOperation import ABCOperation
from neurobehavioral_analytics_suite.operation_manager.operations.computation.DaskOperation import DaskOperation
from neurobehavioral_analytics_suite.operation_manager.operations.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation
from neurobehavioral_analytics_suite.utils.ErrorHandler import ErrorHandler


class UserInputManager:
    """
    A class to process user input from the console.

    This class processes user input and executes corresponding commands, such as stopping, pausing, resuming operations,
    and displaying system resources, tasks, and queue status.
    """

    def __init__(self, operation_control, logger, error_handler: ErrorHandler):
        """
        Initializes the UserInputManager with the necessary components.

        Args:
            operation_control: Control interface for operations.
            logger: CustomLogger instance for logging messages.
            error_handler (ErrorHandler): Error handler for managing errors.
        """
        self.operation_control = operation_control
        self.logger = logger
        self.error_handler = error_handler

    async def process_user_input(self, user_input: str) -> str:
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
            await self.operation_control.stop_all_operations()
            return "UserInputManager.process_user_input: Stopping all operations..."

        elif user_input == "load_data":
            def load_data():
                import dask.dataframe as dd
                df = dd.read_csv("../sample_datasets/2024-Tariq-et-al_olfaction/8-30-2021-2-08 "
                                 "PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor"
                                 "-arenaOct3shuffle1_200000_filtered.csv")
                return df.compute()

            await self.operation_control.operation_manager.add_operation(logger=self.logger,
                                                                         operation_type=DaskOperation,
                                                                         error_handler=self.error_handler,
                                                                         func=load_data,
                                                                         name="LoadData",
                                                                         local_vars=self.operation_control.local_vars,
                                                                         client=dask.distributed.Client())

        elif user_input == "machine_learning":
            self.logger.error("UserInputManager.process_user_input: Machine Learning not implemented.")
            return "UserInputManager.process_user_input: Machine Learning not implemented."

            # ml_operation = MachineLearning(operation_control=self.operation_control,
            # error_handler=self.error_handler) result = await ml_operation.extract_data(
            # file_path="../../../sample_datasets/2024-Tariq-et-al_olfaction/8-30-2021-2-08
            # PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv") print(
            # result) self.logger.info("UserInputManager.process_user_input: Attached machine learning...") data =
            # await ml_operation.extract_data(file_path="../../sample_datasets/2024-Tariq-et-al_olfaction/8-30
            # -2021-2-08 PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv
            # ") train_data, test_data = ml_operation.split_data(data, 7, test_size=0.2)

            # return f"UserInputManager.process_user_input: Attached machine learning..."

        elif user_input == "pause":
            await self.operation_control.pause_all_operations()
            return "UserInputManager.process_user_input: Pausing all operations..."

        elif user_input == "resume":
            await self.operation_control.resume_all_operations()
            return "UserInputManager.process_user_input: Resuming all operations..."

        elif user_input == "resources":
            for operation_list in self.operation_control.queue.queue:
                operation_node = self.operation_control.queue.get_head_operation_from_chain(operation_list)
                if isinstance(operation_node, ResourceMonitorOperation):
                    self.logger.info(operation_node.output_memory_usage())
            return "UserInputManager.process_user_input: Displaying system resources."

        elif user_input == "tasks":
            for task in self.operation_control.task_creator.tasks:
                operation = self.operation_control.queue.find_operation_by_task(task)
                if operation:
                    self.logger.info(f"UserInputManager.process_user_input: Task: {task.get_name()} - "
                                     f"{operation.status}")
            return "UserInputManager.process_user_input: Displaying all tasks..."

        elif user_input == "queue":
            for queue_chain in self.operation_control.queue.queue:
                operation = queue_chain.head.operation
                self.logger.info(f"UserInputManager.process_user_input: Operation: {operation.task.get_name()} - "
                                 f"{operation.status}")
            return "UserInputManager.process_user_input: Displaying all operations in the queue..."

        elif user_input == "vars":
            self.logger.info(f"UserInputManager.process_user_input: Local Vars: {self.operation_control.local_vars}")
            return "UserInputManager.process_user_input: Displaying local vars..."

        else:
            self.logger.info(f"UserInputManager.process_user_input: Executing custom operation with func: {user_input}")
            await self.operation_control.operation_manager.add_operation(operation_type=ABCOperation,
                                                                         func=user_input, name="ConsoleCommand",
                                                                         local_vars=self.operation_control.local_vars,
                                                                         error_handler=self.error_handler,
                                                                         logger=self.logger)
            return f"UserInputManager.process_user_input: Added custom operation with func: {user_input}"
