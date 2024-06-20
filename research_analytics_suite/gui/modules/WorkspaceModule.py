# WorkspaceModule.py

import asyncio
import os
import uuid
from typing import Optional, Any

import dearpygui.dearpygui as dpg

from research_analytics_suite.data_engine.Config import Config
from research_analytics_suite.data_engine.Workspace import Workspace
from research_analytics_suite.operation_manager.OperationControl import OperationControl
from research_analytics_suite.operation_manager.operations.BaseOperation import BaseOperation
from research_analytics_suite.utils.CustomLogger import CustomLogger


class WorkspaceModule:
    """A class to manage the GUI representation of the Workspace."""

    def __init__(self, width: int, height: int):
        """
        Initializes the WorkspaceModule with the given workspace.

        Args:
            width (int): The width of the module.
            height (int): The height of the module.
        """
        self._workspace = Workspace()
        self._logger = CustomLogger()
        self._config = Config()
        self._operation_control = OperationControl()
        self.width = width
        self._user_vars_width = int(self.width * 0.6)
        self._management_width = int(self.width * 0.20)
        self.height = height
        self.update_operation = None
        self.unique_id = str(uuid.uuid4())
        self.user_var_list_id = f"user_var_list_{self.unique_id}"
        self.add_var_dialog_id = None
        self._local_user_vars = {}  # Store user variables

    async def initialize(self) -> None:
        """Initializes resources and sets up the GUI."""
        self.initialize_resources()
        await self.setup_workspace_pane()
        self.update_operation = await self.add_update_operation()

    async def add_update_operation(self) -> Optional[Any]:
        try:
            operation = await self._operation_control.operation_manager.add_operation_with_parameters(
                operation_type=BaseOperation, name="gui_WorkspaceUpdateTask",
                action=self.update_user_variables_list, persistent=True, concurrent=True)
            operation.is_ready = True
            return operation
        except Exception as e:
            self._logger.error(e, self)
        return None

    def initialize_resources(self) -> None:
        """Initializes necessary resources and logs the event."""
        pass

    async def setup_workspace_pane(self) -> None:
        """Sets up the workspace pane asynchronously."""
        with dpg.group(tag="workspace_pane_group", horizontal=True, parent="workspace_group"):
            with dpg.child_window(tag="workspace_management_pane", width=self._management_width, border=True,
                                  parent="workspace_pane_group"):
                dpg.add_text("Workspace Details")
                dpg.add_separator()
                dpg.add_button(label="Save Workspace", callback=self.save_workspace)
                dpg.add_button(label="Load Workspace", callback=self.load_workspace)
                dpg.add_separator()
                dpg.add_text("Workspace Name:")
                dpg.add_input_text(tag="workspace_name_input", default_value=self._config.WORKSPACE_NAME, enabled=False)
                dpg.add_separator()

                dpg.add_text("Save and Restore")
                dpg.add_separator()
                dpg.add_button(label="Save User Variables", callback=self.save_user_variables)
                dpg.add_button(label="Restore User Variables", callback=self.restore_user_variables)
                dpg.add_separator()
                dpg.add_text("Filename:")
                dpg.add_input_text(tag="save_path_input",
                                   default_value=os.path.join('user_variables.db'), width=-1)

            with dpg.child_window(label="User Variables",
                                  tag="user_variables_pane",
                                  width=self._user_vars_width,
                                  border=True, parent="workspace_pane_group"):
                dpg.add_button(label="Add User Variable", callback=self.open_add_var_dialog)
                dpg.add_group(tag=self.user_var_list_id)  # Create the group for user variables list

    async def update_user_variables_list(self) -> None:
        """Updates the user variables list in the GUI."""
        while True:
            try:
                new_user_vars = await self._workspace.list_user_variables()
                new_user_vars_dict = {}

                # Ensure new_user_vars is a dictionary of dictionaries
                if isinstance(new_user_vars, dict):
                    for _memory_id, variables in new_user_vars.items():
                        if isinstance(variables, dict):
                            for name, value in variables.items():
                                if _memory_id not in new_user_vars_dict:
                                    new_user_vars_dict[_memory_id] = {}
                                new_user_vars_dict[_memory_id][name] = value
                        else:
                            raise ValueError("Expected variables to be a dictionary")
                else:
                    raise ValueError("Expected list of user variables to be a dictionary")

                # Remove existing variables that are not in the new list
                for _m_id in list(self._local_user_vars.keys()):
                    # Remove memory slot if it is not in the new list
                    if _m_id not in new_user_vars_dict:
                        # Remove all variables from the memory slot
                        await self.remove_user_variable_from_gui(memory_id=_m_id)
                    else:
                        # Remove variables from the memory slot that are not in the new list
                        for _var_name in list(self._local_user_vars[_m_id].keys()):
                            if _var_name not in new_user_vars_dict[_m_id]:
                                await self.remove_user_variable_from_gui(memory_id=_m_id, var_name=_var_name)
                            else:
                                # Update the value of the variable if it has changed
                                if self._local_user_vars[_m_id][_var_name] != new_user_vars_dict[_m_id][_var_name]:
                                    dpg.set_value(f"user_value_{_m_id}_{_var_name}",
                                                  new_user_vars_dict[_m_id][_var_name])

                # Add and update variables that are in the new list
                for _m_id, variables in new_user_vars_dict.items():
                    if _m_id not in self._local_user_vars.keys():
                        self._local_user_vars[_m_id] = dict()
                    for _var_name, _var_value in variables.items():
                        if _var_name not in self._local_user_vars[_m_id]:
                            await self.add_user_variable_to_gui(memory_id=_m_id, name=_var_name, value=_var_value)
                        else:
                            if self._local_user_vars[_m_id][_var_name] != _var_value:
                                dpg.set_value(f"user_value_{_m_id}_{_var_name}", _var_value)

                # Update the local user variables
                self._local_user_vars = new_user_vars_dict

            except Exception as e:
                self._logger.error(Exception(f"Error updating user variables: {e}", self))
            await asyncio.sleep(0.05)

    async def add_user_variable_to_gui(self, memory_id, name, value) -> None:
        """Adds a user variable to the GUI."""
        with dpg.group(parent=self.user_var_list_id,
                       tag=f"user_group_{memory_id}_{name}",
                       horizontal=True,
                       width=-1):
            dpg.add_text(default_value=f"Name: {name}, Value: ", parent=f"user_group_{memory_id}_{name}")
            dpg.add_text(default_value=value, tag=f"user_value_{memory_id}_{name}", parent=f"user_group_{memory_id}_{name}")
            dpg.add_button(label=f"Remove",
                           callback=lambda: asyncio.create_task(self.remove_user_variable(name)),
                           parent=f"user_group_{memory_id}_{name}")

    async def remove_user_variable_from_gui(self, memory_id, var_name=None) -> None:
        """
        Removes a user variable from the GUI.

        Args:
            memory_id (str): The memory ID of the variable.
            var_name (str, optional): The name of the variable.

        """

        dpg.delete_item(f"user_var_group_{memory_id}")

    async def add_user_variable(self, name, value) -> None:
        """Adds a user variable."""
        try:
            await self._workspace.add_user_variable(name, value)
        except Exception as e:
            self._logger.error(Exception(f"Failed to add user variable '{name}': {e}", self))

    async def remove_user_variable(self, name) -> None:
        """Removes a user variable."""
        try:
            self._logger.debug(f"Removing user variable '{name}'")
            await self._workspace.remove_user_variable(name)

        except Exception as e:
            self._logger.error(Exception(f"Failed to remove user variable '{name}': {e}", self))

    async def save_user_variables(self) -> None:
        """Backups the user variables."""
        try:
            save_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                     dpg.get_value("save_path_input"))
            await self._workspace.save_user_variables(save_path)
            self._logger.debug(f"User variables saved to {save_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save user variables: {e}", self))

    async def restore_user_variables(self) -> None:
        """Restores the user variables."""
        try:
            restore_path = os.path.join(self._config.BASE_DIR, self._config.WORKSPACE_NAME,
                                        dpg.get_value("save_path_input"))
            await self._workspace.restore_user_variables(restore_path)
            self._logger.debug(f"User variables restored from {restore_path}")
        except Exception as e:
            self._logger.error(Exception(f"Failed to restore user variables: {e}", self))

    async def save_workspace(self) -> None:
        """Saves the current workspace."""
        try:
            await self._workspace.save_current_workspace()
            self._logger.info("Workspace saved successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to save current workspace: {e}", self))

    async def load_workspace(self) -> None:
        """Loads a workspace."""
        try:
            workspace_path = dpg.get_value("workspace_path_input")
            await self._workspace.load_workspace(workspace_path)
            self._logger.info("Workspace loaded successfully")
        except Exception as e:
            self._logger.error(Exception(f"Failed to load workspace: {e}", self))

    def open_add_var_dialog(self) -> None:
        """Opens a dialog to add a user variable."""
        if self.add_var_dialog_id is None:
            self.add_var_dialog_id = dpg.generate_uuid()
            with dpg.window(label="Add User Variable", modal=True, tag=self.add_var_dialog_id):
                dpg.add_input_text(label="Variable Name", tag="var_name_input")
                dpg.add_input_text(label="Variable Value", tag="var_value_input")
                dpg.add_button(label="Add", callback=lambda: asyncio.create_task(self.add_user_variable_from_dialog()))
                dpg.add_button(label="Cancel", callback=lambda: dpg.hide_item(self.add_var_dialog_id))
        else:
            dpg.show_item(self.add_var_dialog_id)

    async def add_user_variable_from_dialog(self) -> None:
        """Adds a user variable from the dialog inputs."""
        try:
            name = dpg.get_value("var_name_input")
            value = dpg.get_value("var_value_input")
            await self.add_user_variable(name, value)
            dpg.hide_item(self.add_var_dialog_id)
        except Exception as e:
            self._logger.error(Exception(f"Error adding user variable: {e}", self))
