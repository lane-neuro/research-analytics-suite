"""
DataEngineDialog Module

This module defines the DataEngineDialog class, which creates a dialog for interacting with the DataEngine within the
research analytics suite. It handles the initialization, data import, operation execution, and result display,
providing a user interface for managing data operations.

Author: Lane
"""
import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.engine.UnifiedDataEngine import UnifiedDataEngine
from research_analytics_suite.utils.CustomLogger import CustomLogger


class DataEngineDialog:
    """
    A class to create a dialog for interacting with the DataEngine.
    """
    def __init__(self, data_engine: UnifiedDataEngine):
        """
        Initializes the DataEngineDialog instance.

        Args:
            data_engine (UnifiedDataEngine): The data engine for handling data operations.
        """
        self._data_engine = data_engine
        self._logger = CustomLogger()

    async def initialize(self):
        """
        Initializes the data engine dialog.
        """
        with dpg.group(tag="data_engine_dialog"):
            dpg.add_text("Data Engine Operations", color=(255, 255, 0))

            with dpg.group(horizontal=True):
                dpg.add_button(label="Import Data", callback=self._import_data)
                dpg.add_button(label="Execute Operation", callback=self._execute_operation)
                dpg.add_button(label="Show Results", callback=self._show_results)

            dpg.add_text("", tag="data_engine_status")

            dpg.add_separator()

            dpg.add_text("Workspace", color=(255, 255, 0))
            dpg.add_button(label="Refresh Variables", callback=self._refresh_variables)
            dpg.add_listbox(items=[], label="Variables", tag="variables_list", callback=self._select_variable)
            dpg.add_input_text(label="Variable Value", tag="variable_value_input")
            dpg.add_button(label="Update Variable", callback=self._update_variable)
            dpg.add_text("", tag="workspace_status")

    def _import_data(self, sender, app_data, user_data):
        """
        Imports data into the data engine.

        Args:
            sender: Sender of the import command.
            app_data: Application data.
            user_data: User data.
        """
        data_path = "path/to/data.csv"
        self._data_engine.load_data(data_path)
        dpg.set_value("data_engine_status", f"Data imported from {data_path}")
        self._logger.info(f"Data imported from {data_path}")

    def _execute_operation(self, sender, app_data, user_data):
        """
        Executes an operation on the data engine.

        Args:
            sender: Sender of the execute command.
            app_data: Application data.
            user_data: User data.
        """
        result = self._data_engine.perform_operation("operation_name")
        dpg.set_value("data_engine_status", f"Operation executed: {result}")
        self._logger.info(f"Operation executed: {result}")

    def _show_results(self, sender, app_data, user_data):
        """
        Shows the results of the operations performed on the data engine.

        Args:
            sender: Sender of the show results command.
            app_data: Application data.
            user_data: User data.
        """
        results = self._data_engine.get_results()
        dpg.set_value("data_engine_status", f"Results: {results}")
        self._logger.info(f"Results: {results}")

    def _refresh_variables(self, sender, app_data, user_data):
        """
        Refreshes the list of variables in the workspace.

        Args:
            sender: Sender of the refresh command.
            app_data: Application data.
            user_data: User data.
        """
        variables = self._data_engine.get_variable_names()
        dpg.configure_item("variables_list", items=variables)
        self._logger.info("Variables list refreshed")

    def _select_variable(self, sender, app_data, user_data):
        """
        Selects a variable from the list and displays its current value.

        Args:
            sender: Sender of the select command.
            app_data: Application data.
            user_data: User data.
        """
        variable_name = app_data
        variable_value = self._data_engine.get_variable_value(variable_name)
        dpg.set_value("variable_value_input", variable_value)
        self._logger.info(f"Selected variable: {variable_name} with value {variable_value}")

    def _update_variable(self, sender, app_data, user_data):
        """
        Updates the value of the selected variable in the workspace.

        Args:
            sender: Sender of the update command.
            app_data: Application data.
            user_data: User data.
        """
        variable_name = dpg.get_value("variables_list")
        new_value = dpg.get_value("variable_value_input")
        self._data_engine.set_variable_value(variable_name, new_value)
        dpg.set_value("workspace_status", f"Variable '{variable_name}' updated to {new_value}")
        self._logger.info(f"Variable '{variable_name}' updated to {new_value}")
