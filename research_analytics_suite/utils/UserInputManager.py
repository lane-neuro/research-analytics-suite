"""
UserInputManager Module.

This module defines the UserInputManager class, which processes user input from the console within the research
analytics suite. It handles various commands such as stopping, pausing, and resuming operations, as well as displaying
system resources, tasks, and sequencer status.

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

from research_analytics_suite.operation_manager.operations.BaseOperation import BaseOperation
from research_analytics_suite.operation_manager.operations.computation.DaskOperation import DaskOperation
from research_analytics_suite.operation_manager.operations.persistent.ResourceMonitorOperation import \
    ResourceMonitorOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class UserInputManager:
    """
    A class to process user input from the console.

    This class processes user input and executes corresponding commands, such as stopping, pausing, resuming operations,
    and displaying system resources, tasks, and sequencer status.
    """

    def __init__(self):
        """
        Initializes the UserInputManager with the necessary components.
        """
        from research_analytics_suite.operation_manager.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self._logger = CustomLogger()

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
            await self._operation_control.operation_manager.stop_all_operations()
            return "UserInputManager.process_user_input: Stopping all operations..."

        elif user_input == "load_data":
            def load_data():
                import dask.dataframe as dd
                df = dd.read_csv("../sample_datasets/2024-Tariq-et-al_olfaction/8-30-2021-2-08 "
                                 "PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor"
                                 "-arenaOct3shuffle1_200000_filtered.csv")
                return df.compute()

            await self._operation_control.operation_manager.add_operation(operation_type=DaskOperation,
                                                                          func=load_data,
                                                                          name="LoadData",
                                                                          client=dask.distributed.Client())

        elif user_input == "machine_learning":
            self._logger.error(Exception("UserInputManager.process_user_input: Machine Learning not implemented."))
            return "UserInputManager.process_user_input: Machine Learning not implemented."

            # ml_operation = MachineLearning(_operation_control=self._operation_control
            # ) result = await ml_operation.extract_data(
            # file_path="../../../sample_datasets/2024-Tariq-et-al_olfaction/8-30-2021-2-08
            # PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv") print(
            # result) self._logger.info("UserInputManager.process_user_input: Attached machine learning...") data =
            # await ml_operation.extract_data(file_path="../../sample_datasets/2024-Tariq-et-al_olfaction/8-30
            # -2021-2-08 PM-Mohammad-ETHSensor-CB3-3_reencodedDLC_resnet50_odor-arenaOct3shuffle1_200000_filtered.csv
            # ") train_data, test_data = ml_operation.split_data(data, 7, test_size=0.2)

            # return f"UserInputManager.process_user_input: Attached machine learning..."

        elif user_input == "pause":
            await self._operation_control.operation_manager.pause_all_operations()
            return "UserInputManager.process_user_input: Pausing all operations..."

        elif user_input == "resume":
            await self._operation_control.operation_manager.resume_all_operations()
            return "UserInputManager.process_user_input: Resuming all operations..."

        elif user_input == "resources":
            for operation_list in self._operation_control.sequencer.sequencer:
                operation_node = self._operation_control.sequencer.get_head_operation_from_chain(operation_list)
                if isinstance(operation_node, ResourceMonitorOperation):
                    self._logger.info(operation_node.output_memory_usage())
            return "UserInputManager.process_user_input: Displaying system resources."

        elif user_input == "tasks":
            for task in self._operation_control.task_creator.tasks:
                operation = self._operation_control.sequencer.find_operation_by_task(task)
                if operation:
                    self._logger.info(f"UserInputManager.process_user_input: Task: {task.get_name()} - "
                                      f"{operation.status}")
            return "UserInputManager.process_user_input: Displaying all tasks..."

        elif user_input == "sequencer":
            for sequencer_chain in self._operation_control.sequencer.sequencer:
                operation = sequencer_chain.head.operation
                self._logger.info(f"UserInputManager.process_user_input: Operation: {operation.task.get_name()} - "
                                  f"{operation.status}")
            return "UserInputManager.process_user_input: Displaying all operations in the sequencer..."

        elif user_input == "vars":

            return "UserInputManager.process_user_input: Displaying local vars..."

        else:
            self._logger.info(f"UserInputManager.process_user_input: Executing custom operation with func: {user_input}")
            await self._operation_control.operation_manager.add_operation(operation_type=BaseOperation,
                                                                          func=user_input, name="ConsoleCommand")
            return f"UserInputManager.process_user_input: Added custom operation with func: {user_input}"
